document.addEventListener('DOMContentLoaded', () => {
    const generateButton = document.getElementById('generate-portfolio');
    const saveButton = document.getElementById('save-portfolio');
    const riskLevelInput = document.getElementById('risk-level');
    const allocationTableBody = document.querySelector('#allocation-table tbody');
    const riskValueDisplay = document.querySelector('.risk-value');
    const ctx = document.getElementById('allocation-chart').getContext('2d');

    let allocationChart;

    // Update risk level display
    riskValueDisplay.textContent = riskLevelInput.value;
    riskLevelInput.addEventListener('input', () => {
        riskValueDisplay.textContent = riskLevelInput.value;
    });

    // Generate portfolio
    generateButton.addEventListener('click', async () => {
        const name = document.getElementById('portfolio-name').value.trim();
        const description = document.getElementById('portfolio-description').value.trim();
        const riskLevel = parseInt(riskLevelInput.value);
        const initialInvestment = parseFloat(document.getElementById('initial-investment').value);

        if (!name || isNaN(initialInvestment) || initialInvestment <= 0) {
            alert('Please provide valid inputs.');
            return;
        }

        try {
            const response = await fetch('http://localhost:8000/portfolios/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name,
                    description,
                    risk_level: riskLevel,
                    initial_investment: initialInvestment,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to generate portfolio.');
            }

            const data = await response.json();
            displayAllocations(data.allocations);
            updateChart(data.allocations);
            saveButton.disabled = false;
        } catch (error) {
            console.error(error);
            alert('Error generating portfolio. Please try again later.');
        }
    });

    function displayAllocations(allocations) {
        allocationTableBody.innerHTML = '';
        allocations.forEach(allocation => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${allocation.asset_name}</td>
                <td>${allocation.asset_type}</td>
                <td>${allocation.percentage.toFixed(2)}%</td>
                <td>$${allocation.current_value.toFixed(2)}</td>
            `;
            allocationTableBody.appendChild(row);
        });
    }

    function updateChart(allocations) {
        const labels = allocations.map(a => a.asset_name);
        const data = allocations.map(a => a.percentage);

        if (allocationChart) {
            allocationChart.destroy();
        }

        allocationChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
                }],
            },
        });
    }
});