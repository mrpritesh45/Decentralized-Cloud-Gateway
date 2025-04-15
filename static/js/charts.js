function createResourceUsageChart() {
    const ctx = document.getElementById('resource-usage-chart');
    
    if (!ctx) return;
    
    // Fetch resource data
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            window.resourceUsageChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['CPU (cores)', 'Memory (GB)', 'Storage (GB)'],
                    datasets: [
                        {
                            label: 'Allocated',
                            data: [
                                stats.allocated_resources.cpu,
                                stats.allocated_resources.memory,
                                stats.allocated_resources.storage
                            ],
                            backgroundColor: 'rgba(255, 99, 132, 0.8)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Available',
                            data: [
                                stats.available_resources.cpu,
                                stats.available_resources.memory,
                                stats.available_resources.storage
                            ],
                            backgroundColor: 'rgba(54, 162, 235, 0.8)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Amount'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Resource Type'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching resource data:', error));
}

function createRequestStatusChart() {
    const ctx = document.getElementById('request-status-chart');
    
    if (!ctx) return;
    
    // Fetch request data
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            window.requestStatusChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Pending', 'Approved', 'Completed'],
                    datasets: [{
                        data: [
                            stats.pending_requests,
                            stats.approved_requests,
                            stats.completed_requests
                        ],
                        backgroundColor: [
                            'rgba(255, 205, 86, 0.8)',  // Yellow for pending
                            'rgba(75, 192, 192, 0.8)',  // Green for approved
                            'rgba(54, 162, 235, 0.8)'   // Blue for completed
                        ],
                        borderColor: [
                            'rgba(255, 205, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(54, 162, 235, 1)'
                        ],
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
                        title: {
                            display: true,
                            text: 'Resource Request Status'
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching request data:', error));
}
