// Environmental Dashboard JavaScript
class EnvironmentalDashboard {
    constructor() {
        this.data = {
            years: [1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024],
            co2_levels: [338.7, 345.9, 354.4, 360.9, 369.5, 379.8, 389.9, 400.8, 414.2, 421.1],
            temperature_anomaly: [-0.2, -0.1, 0.4, 0.4, 0.4, 0.7, 0.7, 0.9, 1.0, 1.2],
            sea_level_mm: [0, 15, 30, 45, 65, 85, 110, 135, 165, 185],
            forest_cover_pct: [31.2, 30.8, 30.3, 29.9, 29.4, 28.9, 28.4, 27.9, 27.4, 27.0],
            arctic_ice_extent: [7.2, 7.0, 6.8, 6.5, 6.2, 5.8, 5.4, 4.9, 4.3, 4.1]
        };

this.keyEvents = [
    {year: 1972, event: "Stockholm Conference", type: "policy"},
    {year: 1987, event: "Montreal Protocol", type: "policy"},
    {year: 1988, event: "IPCC Established", type: "policy"},
    {year: 1992, event: "Rio Earth Summit", type: "policy"},
    {year: 1997, event: "Kyoto Protocol", type: "policy"},
    // {year: 2006, event: "Al Gore's 'An Inconvenient Truth'", type: "awareness"},
    {year: 2010, event: "Deepwater Horizon Oil Spill", type: "disaster"},
    {year: 2012, event: "Arctic Sea Ice Minimum", type: "climate"},
    {year: 2015, event: "Paris Agreement", type: "policy"},
    // {year: 2016, event: "David Attenborough's Planet Earth II", type: "awareness"},
    {year: 2018, event: "IPCC 1.5°C Report", type: "science"},
    // {year: 2019, event: "Global Climate Strikes", type: "movement"},
    {year: 2019, event: "Amazon Rainforest Fires", type: "disaster"},
    // {year: 2020, event: "COVID-19 Impact", type: "event"},
    // {year: 2021, event: "COP26 Glasgow Pact", type: "policy"},
    {year: 2022, event: "Pakistan Floods", type: "climate"},
    {year: 2023, event: "Hottest Year on Record", type: "climate"},
    // {year: 2023, event: "UN Plastic Treaty Talks", type: "policy"},
    // {year: 2023, event: "James Webb Telescope Climate Data", type: "science"},
    // {year: 2024, event: "Fridays for Future Global March", type: "movement"}
];
        this.regionalData = [
            {region: "Arctic", temp_change: 2.3, impact_level: "critical"},
            {region: "Amazon", deforestation: 15.2, impact_level: "high"},
            {region: "Pacific Islands", sea_level_impact: 8.5, impact_level: "critical"},
            {region: "Sahara", desertification: 12.1, impact_level: "moderate"},
            {region: "Antarctica", ice_loss: 18.7, impact_level: "high"}
        ];

        this.charts = {};
        this.currentFilter = 'all';
        this.currentDateRange = 'all';

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.createTimeline();
        this.createCharts();
        this.createMiniCharts();
        this.updateLastUpdated();
        this.animateCounters();
    }

    setupEventListeners() {
        // Timeline filter buttons
        document.querySelectorAll('.timeline-filter').forEach(button => {
            button.addEventListener('click', (e) => {
                this.filterTimeline(e.target.dataset.filter);
            });
        });

        // Date range selector
        const dateRangeSelect = document.getElementById('dateRange');
        if (dateRangeSelect) {
            dateRangeSelect.addEventListener('change', (e) => {
                this.updateDateRange(e.target.value);
            });
        }

        // Hotspot interactions
        document.querySelectorAll('.climate-hotspot').forEach(hotspot => {
            hotspot.addEventListener('click', (e) => {
                this.showHotspotDetails(e.target.closest('.climate-hotspot').dataset.location);
            });
        });

        // Smooth scrolling for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    createTimeline() {
        const timelineContainer = document.getElementById('timelineEvents');
        if (!timelineContainer) return;

        timelineContainer.innerHTML = '';

        this.keyEvents.forEach(event => {
            const eventElement = document.createElement('div');
            eventElement.className = `timeline-event ${event.type}`;
            eventElement.innerHTML = `
                <div class="timeline-marker ${event.type}"></div>
                <div class="timeline-content">
                    <div class="timeline-year">${event.year}</div>
                    <div class="timeline-title">${event.event}</div>
                </div>
            `;
            timelineContainer.appendChild(eventElement);
        });
    }

    filterTimeline(filter) {
        this.currentFilter = filter;
        
        // Update active button
        document.querySelectorAll('.timeline-filter').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');

        // Filter events
        document.querySelectorAll('.timeline-event').forEach(event => {
            if (filter === 'all' || event.classList.contains(filter)) {
                event.style.display = 'flex';
            } else {
                event.style.display = 'none';
            }
        });
    }

    getFilteredData() {
        let startIndex = 0;
        let endIndex = this.data.years.length;

        switch (this.currentDateRange) {
            case 'recent':
                startIndex = this.data.years.findIndex(year => year >= 2010);
                break;
            case 'decade':
                startIndex = this.data.years.findIndex(year => year >= 2015);
                break;
        }

        return {
            years: this.data.years.slice(startIndex, endIndex),
            co2_levels: this.data.co2_levels.slice(startIndex, endIndex),
            temperature_anomaly: this.data.temperature_anomaly.slice(startIndex, endIndex),
            sea_level_mm: this.data.sea_level_mm.slice(startIndex, endIndex),
            forest_cover_pct: this.data.forest_cover_pct.slice(startIndex, endIndex),
            arctic_ice_extent: this.data.arctic_ice_extent.slice(startIndex, endIndex)
        };
    }

    createCharts() {
        const filteredData = this.getFilteredData();

        // CO2 Chart
        this.createCO2Chart(filteredData);
        
        // Temperature Chart
        this.createTemperatureChart(filteredData);
        
        // Regional Chart
        this.createRegionalChart();
        
        // Combined Chart
        this.createCombinedChart(filteredData);
    }

    createCO2Chart(data) {
        const ctx = document.getElementById('co2Chart');
        if (!ctx) return;

        if (this.charts.co2) {
            this.charts.co2.destroy();
        }

        this.charts.co2 = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.years,
                datasets: [{
                    label: 'CO₂ Concentration (ppm)',
                    data: data.co2_levels,
                    borderColor: '#FF6B35',
                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'CO₂ (ppm)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Year'
                        }
                    }
                }
            }
        });
    }

    createTemperatureChart(data) {
        const ctx = document.getElementById('tempChart');
        if (!ctx) return;

        if (this.charts.temperature) {
            this.charts.temperature.destroy();
        }

        this.charts.temperature = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.years,
                datasets: [{
                    label: 'Temperature Anomaly (°C)',
                    data: data.temperature_anomaly,
                    borderColor: '#DC143C',
                    backgroundColor: 'rgba(220, 20, 60, 0.2)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Temperature Anomaly (°C)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Year'
                        }
                    }
                }
            }
        });
    }

    createRegionalChart() {
        const ctx = document.getElementById('regionalChart');
        if (!ctx) return;

        if (this.charts.regional) {
            this.charts.regional.destroy();
        }

        const impactValues = this.regionalData.map(region => {
            switch(region.impact_level) {
                case 'critical': return 10;
                case 'high': return 7;
                case 'moderate': return 4;
                default: return 1;
            }
        });

        this.charts.regional = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.regionalData.map(r => r.region),
                datasets: [{
                    label: 'Environmental Impact Level',
                    data: impactValues,
                    backgroundColor: [
                        '#DC143C',
                        '#FF6B35',
                        '#DC143C',
                        '#32CD32',
                        '#FF6B35'
                    ],
                    borderColor: [
                        '#DC143C',
                        '#FF6B35',
                        '#DC143C',
                        '#32CD32',
                        '#FF6B35'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        title: {
                            display: true,
                            text: 'Impact Level'
                        }
                    }
                }
            }
        });
    }

    createCombinedChart(data) {
        const ctx = document.getElementById('combinedChart');
        if (!ctx) return;

        if (this.charts.combined) {
            this.charts.combined.destroy();
        }

        this.charts.combined = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.years,
                datasets: [{
                    label: 'Sea Level Rise (mm)',
                    data: data.sea_level_mm,
                    borderColor: '#1E90FF',
                    backgroundColor: 'rgba(30, 144, 255, 0.1)',
                    yAxisID: 'y'
                }, {
                    label: 'Forest Cover (%)',
                    data: data.forest_cover_pct,
                    borderColor: '#228B22',
                    backgroundColor: 'rgba(34, 139, 34, 0.1)',
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Year'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Sea Level (mm)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Forest Cover (%)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    }

    createMiniCharts() {
        // CO2 Mini Chart
        this.createMiniChart('co2-mini-chart', this.data.co2_levels.slice(-5), '#FF6B35');
        
        // Temperature Mini Chart
        this.createMiniChart('temp-mini-chart', this.data.temperature_anomaly.slice(-5), '#DC143C');
    }

    createMiniChart(elementId, data, color) {
        const container = document.getElementById(elementId);
        if (!container) return;

        const canvas = document.createElement('canvas');
        canvas.width = 120;
        canvas.height = 40;
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array.from({length: data.length}, (_, i) => i),
                datasets: [{
                    data: data,
                    borderColor: color,
                    backgroundColor: color + '20',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                elements: {
                    point: { radius: 0 }
                }
            }
        });
    }

    updateDateRange(range) {
        this.currentDateRange = range;
        this.createCharts();
    }

    showHotspotDetails(location) {
        const locationData = this.regionalData.find(r => 
            r.region.toLowerCase().includes(location.toLowerCase())
        );
        
        if (locationData) {
            const message = `${locationData.region}: Impact Level - ${locationData.impact_level.toUpperCase()}`;
            
            // Create a temporary notification
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #2E8B57;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                z-index: 1000;
                animation: slideIn 0.3s ease;
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
    }

    updateLastUpdated() {
        const now = new Date();
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        const dateString = now.toLocaleDateString('en-US', options);
        
        const elements = document.querySelectorAll('#lastUpdated, #footerLastUpdated');
        elements.forEach(el => {
            if (el) el.textContent = dateString;
        });
    }

    animateCounters() {
        const counters = document.querySelectorAll('.metric-value .value');
        
        const animateValue = (element, start, end, duration) => {
            let startTimestamp = null;
            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                const current = progress * (end - start) + start;
                element.textContent = Math.floor(current * 10) / 10;
                if (progress < 1) {
                    window.requestAnimationFrame(step);
                }
            };
            window.requestAnimationFrame(step);
        };

        // Animate counters when they come into view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const endValue = parseFloat(element.dataset.value || element.textContent);
                    animateValue(element, 0, endValue, 2000);
                    observer.unobserve(element);
                }
            });
        });

        counters.forEach(counter => {
            counter.dataset.value = counter.textContent;
            observer.observe(counter);
        });
    }

    // Method to refresh all data (could be called periodically)
    refreshData() {
        // In a real application, this would fetch new data from an API
        console.log('Refreshing environmental data...');
        this.updateLastUpdated();
        
        // Simulate data update with slight variations
        const lastIndex = this.data.years.length - 1;
        this.data.co2_levels[lastIndex] += Math.random() * 0.1 - 0.05;
        this.data.temperature_anomaly[lastIndex] += Math.random() * 0.02 - 0.01;
        
        // Update charts
        this.createCharts();
        this.createMiniCharts();
    }

    // Method to export data (could be useful for users)
    exportData() {
        const dataToExport = {
            environmental_data: this.data,
            key_events: this.keyEvents,
            regional_data: this.regionalData,
            export_date: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(dataToExport, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'environmental_data.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new EnvironmentalDashboard();
    
    // Add some additional interactive features
    
    // Add CSS for notifications
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .notification {
            animation: slideIn 0.3s ease;
        }
    `;
    document.head.appendChild(style);
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'r':
                    e.preventDefault();
                    window.dashboard.refreshData();
                    break;
                case 'e':
                    e.preventDefault();
                    window.dashboard.exportData();
                    break;
            }
        }
    });
    
    // Add scroll-based animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Apply fade-in animation to cards and sections
    document.querySelectorAll('.metric-card, .chart-container, .insight-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        fadeInObserver.observe(el);
    });
    
    // Add periodic data refresh (every 5 minutes in a real app)
    // setInterval(() => {
    //     window.dashboard.refreshData();
    // }, 300000);
});

// Add some utility functions
window.utils = {
    formatNumber: (num, decimals = 1) => {
        return Number(num).toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },
    
    formatDate: (date) => {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    getImpactColor: (level) => {
        const colors = {
            critical: '#DC143C',
            high: '#FF6B35',
            moderate: '#32CD32',
            low: '#228B22'
        };
        return colors[level] || '#8FBC8F';
    }
};