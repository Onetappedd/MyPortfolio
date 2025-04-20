document.addEventListener('DOMContentLoaded', () => {
    // Fetch skills from API
    fetchSkills();
    
    // Fetch projects from API
    fetchProjects();
    
    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Form submission handler
    const contactForm = document.querySelector('.contact-form form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! This is a demo form, so no message was actually sent.');
            this.reset();
        });
    }
});

// Fetch skills from the API
async function fetchSkills() {
    try {
        const response = await fetch('http://localhost:8000/skills');
        const skills = await response.json();
        
        displaySkills(skills);
    } catch (error) {
        console.error('Error fetching skills:', error);
        document.getElementById('skills-list').innerHTML = `
            <p>Failed to load skills. Please try again later.</p>
            <p>If you're running this locally, make sure the API is running at http://localhost:8000</p>
        `;
    }
}

// Display skills in the UI
function displaySkills(skills) {
    const skillsContainer = document.getElementById('skills-list');
    
    if (skills.length === 0) {
        skillsContainer.innerHTML = '<p>No skills found.</p>';
        return;
    }
    
    skillsContainer.innerHTML = '';
    
    skills.forEach(skill => {
        const skillElement = document.createElement('div');
        skillElement.className = 'skill-item';
        
        skillElement.innerHTML = `
            <div class="skill-name">${skill.name}</div>
            <div class="skill-bar">
                <div class="skill-level" style="width: ${skill.proficiency}%"></div>
            </div>
            <div class="skill-category">${skill.category}</div>
        `;
        
        skillsContainer.appendChild(skillElement);
    });
}

// Fetch projects from the API
async function fetchProjects() {
    try {
        const response = await fetch('http://localhost:8000/projects');
        const projects = await response.json();
        
        displayProjects(projects);
    } catch (error) {
        console.error('Error fetching projects:', error);
        document.getElementById('projects-grid').innerHTML = `
            <p>Failed to load projects. Please try again later.</p>
            <p>If you're running this locally, make sure the API is running at http://localhost:8000</p>
        `;
    }
}

// Display projects in the UI
function displayProjects(projects) {
    const projectsGrid = document.getElementById('projects-grid');
    
    if (projects.length === 0) {
        projectsGrid.innerHTML = '<p>No projects found.</p>';
        return;
    }
    
    projectsGrid.innerHTML = '';
    
    projects.forEach(project => {
        const projectElement = document.createElement('div');
        projectElement.className = 'project-card';
        
        // Use a placeholder image if the project image is not available
        const imageUrl = project.image_url || 'https://via.placeholder.com/300x200?text=Project+Image';
        
        // Create HTML for project technologies
        const techTags = project.technologies.map(tech => `
            <span class="tech-tag">${tech}</span>
        `).join('');
        
        // Create HTML for project links
        let linksHTML = '';
        
        if (project.project_url) {
            linksHTML += `<a href="${project.project_url}" target="_blank">Live Demo</a>`;
        }
        
        if (project.github_url) {
            linksHTML += `<a href="${project.github_url}" target="_blank">GitHub</a>`;
        }
        
        projectElement.innerHTML = `
            <img src="${imageUrl}" alt="${project.title}" class="project-image">
            <div class="project-info">
                <h3 class="project-title">${project.title}</h3>
                <p class="project-description">${project.description}</p>
                <div class="project-tech">
                    ${techTags}
                </div>
                <div class="project-links">
                    ${linksHTML}
                </div>
            </div>
        `;
        
        projectsGrid.appendChild(projectElement);
    });
}

// Add header scroll effect
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        header.style.background = 'rgba(255, 255, 255, 0.95)';
    } else {
        header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        header.style.background = 'white';
    }
});

// Update your name in the portfolio
document.addEventListener('DOMContentLoaded', () => {
    // Change this to your name
    const yourName = "Your Name";
    
    // Update name in the hero section
    const nameElement = document.getElementById('name');
    if (nameElement) {
        nameElement.textContent = yourName;
    }
    
    // Update copyright in footer
    const footerText = document.querySelector('footer p');
    if (footerText) {
        footerText.textContent = `© ${new Date().getFullYear()} ${yourName} - All Rights Reserved`;
    }
});