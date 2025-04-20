document.addEventListener('DOMContentLoaded', () => {
    const portfolioSelect = document.getElementById('portfolio-select');
    const refreshButton = document.getElementById('refresh-portfolio');
    const editButton = document.getElementById('edit-portfolio');
    const deleteButton = document.getElementById('delete-portfolio');
    
    let currentPortfolio = null;
    let allocationChart = null;
    
    // Modal elements
    const editModal = document.getElementById('edit-modal');
    const deleteModal = document.getElementById('delete-modal');
    const closeButtons = document.querySelectorAll('.close-modal');
    const confirmDeleteButton = document.getElementById('confirm-delete');
    const cancelDeleteButton = document.getElementById('cancel-delete');
    
    // Fetch all portfolios on page load
    fetchPortfolios();
    
    // Refresh button click handler
    refreshButton.addEventListener('click', () => {
        if (currentPortfolio) {
            fetchPortfolio(currentPortfolio.id);
        } else {
            fetchPortfolios();
        }
    });
    
    // Portfolio selection change handler
    portfolioSelect.addEventListener('change', () => {
        const portfolioId = portfolioSelect.value;
        if (portfolioId) {
            fetchPortfolio(portfolioId);
        } else {
            clearDashboard();
        }
    });
    
    // Edit button click handler
    editButton.addEventListener('click', () => {
        if (currentPortfolio) {
            // Populate the edit form
            document.getElementById('edit-name').value = currentPortfolio.name;
            document.getElementById('edit-description').value = currentPortfolio.description || '';
            const editRiskLevel = document.getElementById('edit-risk-level');
            editRiskLevel.value = currentPortfolio.risk_level;
            document.getElementById('edit-risk-value').textContent = currentPortfolio.risk_level;
            
            // Show the edit modal
            editModal.style.display = 'block';
        }
    });
    
    // Delete button click handler
    deleteButton.addEventListener('click', () => {
        if (currentPortfolio) {
            deleteModal.style.display = 'block';
        }
    });
    
    // Modal close handlers
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            editModal.style.display = 'none';
            deleteModal.style.display = 'none';
        });
    });
    
    // Edit form submission handler
    document.getElementById('edit-portfolio-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!currentPortfolio) return;
        
        const name = document.getElementById('edit-name').value.trim();
        const description = document.getElementById('edit-description').value.trim();
        const riskLevel = parseInt(document.getElementById('edit-risk-level').value);
        
        if (!name) {
            alert('Please enter a portfolio name');
            return;
        }
        
        try {
            const response = await fetch(`http://localhost:8000/portfolios/${currentPortfolio.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    description,
                    risk_level: riskLevel,
                    initial_investment: currentPortfolio.initial_investment
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to update portfolio');
            }
            
            // Close the modal and refresh the portfolio
            editModal.style.display = 'none';
            fetchPortfolio(currentPortfolio.id);
            fetchPortfolios(); // Update the dropdown list too
            
        } catch (error) {
            console.error('Error updating portfolio:', error);
            alert('Error updating portfolio. Please try again later.');
        }
    });
    
    // Risk level slider in edit modal
    document.getElementById('edit-risk-level').addEventListener('input', (e) => {
        document.getElementById('edit-risk-value').textContent = e.target.value;
    });
    
    // Confirm delete handler
    confirmDeleteButton.addEventListener('click', async () => {
        if (!currentPortfolio) return;
        
        try {
            const response = await fetch(`http://localhost:8000/portfolios/${currentPortfolio.id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete portfolio');
            }
            
            // Close the modal and refresh the portfolios list
            deleteModal.style.display = 'none';
            clearDashboard();
            fetchPortfolios();
            
        } catch (error) {
            console.error('Error deleting portfolio:', error);
            alert('Error deleting portfolio. Please try again later.');
        }
    });
    
    // Cancel delete handler
    cancelDeleteButton.addEventListener('click', () => {
        deleteModal.style.display = 'none';
    });
    
    // Click outside modal to close
    window.addEventListener('click', (e) => {
        if (e.target === editModal) {
            editModal.style.display = 'none';
        }
        if (e.target === deleteModal) {
            deleteModal.style.display = 'none';
        }
    });
    
    // Fetch all portfolios from API
    async function fetchPortfolios() {
        try {
            const response = await fetch('http://localhost:8000/portfolios');
            
            if (!response.ok) {
                throw new Error('Failed to fetch portfolios');
            }
            
            const portfolios = await response.json();
            
            // Update the portfolio selector
            portfolioSelect.innerHTML = '';
            
            if (portfolios.length === 0) {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No portfolios found';
                portfolioSelect.appendChild(option);
            } else {
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = 'Select a portfolio';
                portfolioSelect.appendChild(defaultOption);
                
                portfolios.forEach(portfolio => {
                    const option = document.createElement('option');
                    option.value = portfolio.id;
                    option.textContent = portfolio.name;
                    portfolioSelect.appendChild(option);
                    
                    // If this portfolio was previously selected, select it again
                    if (currentPortfolio && portfolio.id === currentPortfolio.id) {
                        option.selected = true;
                    }
                });
            }
            
        } catch (error) {
            console.error('Error fetching portfolios:', error);
            portfolioSelect.innerHTML = '<option value="">Error loading portfolios</option>';
        }
    }
    
    // Fetch a specific portfolio by ID
    async function fetchPortfolio(portfolioId) {
        try {
            const response = await fetch(`http://localhost:8000/portfolios/${portfolioId}`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch portfolio');
            }
            
            const portfolio = await response.json();
            currentPortfolio = portfolio;
            
            // Update the dashboard with portfolio data
            updateDashboard(portfolio);
            
        } catch (error) {
            console.error('Error fetching portfolio:', error);
            alert('Error fetching portfolio details. Please try again later.');
        }
    }
    
    // Update dashboard with portfolio data
    function updateDashboard(portfolio) {
        // Portfolio header
        document.getElementById('portfolio-name-display').textContent = portfolio.name;
        document.getElementById('portfolio-description-display').textContent = portfolio.description || 'No description provided';
        
        // Portfolio metrics
        let totalValue = 0;
        portfolio.allocations.forEach(allocation => {
            totalValue += allocation.current_value || 0;
        });
        
        document.getElementById('total-value').textContent = `$${totalValue.toFixed(2)}`;
        document.getElementById('risk-level-display').textContent = `${portfolio.risk_level}/10`;
        
        const createdDate = new Date(portfolio.created_at);
        document.getElementById('created-date').textContent = createdDate.toLocaleDateString();
        
        // Enable action buttons
        editButton.disabled = false;
        deleteButton.disabled = false;
        
        // Update allocation chart
        updateAllocationChart(portfolio);
        
        // Update allocation table
        updateAllocationTable(portfolio);
    }
    
    // Update allocation chart
    function updateAllocationChart(portfolio) {
        // Group allocations by asset type
        const assetTypes = {};
        const colors = {
            'stock': 'rgba(54, 162, 235, 0.8)',
            'bond': 'rgba(255, 206, 86, 0.8)',
            'cash': 'rgba(75, 192, 192, 0.8)',
            'real_estate': 'rgba(153, 102, 255, 0.8)'
        };
        
        portfolio.allocations.forEach(allocation => {
            const type = allocation.asset_type;
            if (!assetTypes[type]) {
                assetTypes[type] = 0;
            }
            assetTypes[type] += allocation.percentage;
        });
        
        // Prepare data for the chart
        const labels = Object.keys(assetTypes);
        const data = labels.map(label => assetTypes[label]);
        const backgroundColor = labels.map(label => colors[label] || 'rgba(201, 203, 207, 0.8)');
        
        // Create or update the chart
        const ctx = document.getElementById('dashboard-allocation-chart').getContext('2d');
        
        if (allocationChart) {
            allocationChart.destroy();
        }
        
        allocationChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels.map(label => label.charAt(0).toUpperCase() + label.slice(1)),
                datasets: [{
                    data: data,
                    backgroundColor: backgroundColor,
                    borderColor: 'white',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value.toFixed(2)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Update allocation table
    function updateAllocationTable(portfolio) {
        const tbody = document.getElementById('dashboard-allocation-table').querySelector('tbody');
        tbody.innerHTML = '';
        
        if (portfolio.allocations.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="5" class="empty-state">No allocations found</td>';
            tbody.appendChild(row);
            return;
        }
        
        portfolio.allocations.sort((a, b) => b.percentage - a.percentage).forEach(allocation => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${allocation.asset_name}</td>
                <td>${allocation.asset_type.charAt(0).toUpperCase() + allocation.asset_type.slice(1)}</td>
                <td>${allocation.ticker || 'N/A'}</td>
                <td>${allocation.percentage.toFixed(2)}%</td>
                <td>$${allocation.current_value.toFixed(2)}</td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    // Clear dashboard when no portfolio is selected
    function clearDashboard() {
        currentPortfolio = null;
        
        // Reset header and metrics
        document.getElementById('portfolio-name-display').textContent = 'Select a portfolio';
        document.getElementById('portfolio-description-display').textContent = '';
        document.getElementById('total-value').textContent = '$0.00';
        document.getElementById('risk-level-display').textContent = '-';
        document.getElementById('created-date').textContent = '-';
        
        // Disable action buttons
        editButton.disabled = true;
        deleteButton.disabled = true;
        
        // Clear chart
        if (allocationChart) {
            allocationChart.destroy();
            allocationChart = null;
        }
        
        // Clear table
        const tbody = document.getElementById('dashboard-allocation-table').querySelector('tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Select a portfolio to view holdings</td></tr>';
    }
});