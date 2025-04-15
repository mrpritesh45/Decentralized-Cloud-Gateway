document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    createResourceUsageChart();
    createRequestStatusChart();
    
    // Refresh data every 30 seconds
    setInterval(refreshData, 30000);
});

function refreshData() {
    // Fetch updated stats
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
            updateCharts(data);
        })
        .catch(error => console.error('Error fetching stats:', error));
}

function updateDashboardStats(stats) {
    // Update user count
    document.getElementById('user-count').textContent = stats.user_count;
    
    // Update resource count
    document.getElementById('resource-count').textContent = stats.resource_count;
    
    // Update request count
    document.getElementById('request-count').textContent = stats.request_count;
    
    // Update CPU available
    document.getElementById('cpu-available').textContent = stats.available_resources.cpu.toFixed(2);
    
    // Update memory available
    document.getElementById('memory-available').textContent = stats.available_resources.memory.toFixed(2);
    
    // Update storage available
    document.getElementById('storage-available').textContent = stats.available_resources.storage.toFixed(2);
    
    // Update resource utilization rates
    document.getElementById('cpu-utilization').textContent = stats.utilization_rate.cpu.toFixed(2) + '%';
    document.getElementById('memory-utilization').textContent = stats.utilization_rate.memory.toFixed(2) + '%';
    document.getElementById('storage-utilization').textContent = stats.utilization_rate.storage.toFixed(2) + '%';
    
    // Update progress bars
    document.getElementById('cpu-progress').style.width = stats.utilization_rate.cpu + '%';
    document.getElementById('memory-progress').style.width = stats.utilization_rate.memory + '%';
    document.getElementById('storage-progress').style.width = stats.utilization_rate.storage + '%';
}

function updateCharts(stats) {
    // Update charts with new data
    if (window.resourceUsageChart) {
        window.resourceUsageChart.data.datasets[0].data = [
            stats.allocated_resources.cpu,
            stats.allocated_resources.memory,
            stats.allocated_resources.storage
        ];
        window.resourceUsageChart.data.datasets[1].data = [
            stats.available_resources.cpu,
            stats.available_resources.memory,
            stats.available_resources.storage
        ];
        window.resourceUsageChart.update();
    }
    
    if (window.requestStatusChart) {
        window.requestStatusChart.data.datasets[0].data = [
            stats.pending_requests,
            stats.approved_requests,
            stats.completed_requests
        ];
        window.requestStatusChart.update();
    }
}
