document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for resource management
    setupResourceButtons();
});

function setupResourceButtons() {
    // Setup delete resource buttons
    document.querySelectorAll('.delete-resource-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const resourceId = this.getAttribute('data-resource-id');
            if (confirm('Are you sure you want to delete this resource?')) {
                deleteResource(resourceId);
            }
        });
    });
    
    // Setup edit resource buttons
    document.querySelectorAll('.edit-resource-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const resourceId = this.getAttribute('data-resource-id');
            const resourceRow = document.querySelector(`tr[data-resource-id="${resourceId}"]`);
            
            // Get current values
            const type = resourceRow.querySelector('.resource-type').textContent;
            const amount = parseFloat(resourceRow.querySelector('.resource-amount').textContent);
            const availability = resourceRow.querySelector('.resource-availability').textContent === 'Available';
            
            // Populate edit form
            document.getElementById('edit-resource-id').value = resourceId;
            document.getElementById('edit-resource-type').value = type.toLowerCase();
            document.getElementById('edit-resource-amount').value = amount;
            document.getElementById('edit-resource-availability').checked = availability;
            
            // Show edit modal
            const editModal = new bootstrap.Modal(document.getElementById('editResourceModal'));
            editModal.show();
        });
    });
    
    // Setup save edit button
    const saveEditBtn = document.getElementById('save-edit-btn');
    if (saveEditBtn) {
        saveEditBtn.addEventListener('click', function() {
            const resourceId = document.getElementById('edit-resource-id').value;
            const resourceType = document.getElementById('edit-resource-type').value;
            const amount = parseFloat(document.getElementById('edit-resource-amount').value);
            const availability = document.getElementById('edit-resource-availability').checked;
            
            updateResource(resourceId, resourceType, amount, availability);
        });
    }
}

function deleteResource(resourceId) {
    fetch(`/api/delete-resource/${resourceId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove resource row from table
            const resourceRow = document.querySelector(`tr[data-resource-id="${resourceId}"]`);
            if (resourceRow) {
                resourceRow.remove();
            }
            
            // Show success message
            showAlert('Resource deleted successfully', 'success');
        } else {
            // Show error message
            showAlert(`Error: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        console.error('Error deleting resource:', error);
        showAlert('An error occurred while deleting the resource', 'danger');
    });
}

function updateResource(resourceId, resourceType, amount, availability) {
    fetch(`/api/update-resource/${resourceId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            resource_type: resourceType,
            amount: amount,
            availability: availability
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update resource row in table
            const resourceRow = document.querySelector(`tr[data-resource-id="${resourceId}"]`);
            if (resourceRow) {
                resourceRow.querySelector('.resource-type').textContent = resourceType.charAt(0).toUpperCase() + resourceType.slice(1);
                resourceRow.querySelector('.resource-amount').textContent = amount;
                resourceRow.querySelector('.resource-availability').textContent = availability ? 'Available' : 'Not Available';
            }
            
            // Hide modal
            const editModal = bootstrap.Modal.getInstance(document.getElementById('editResourceModal'));
            editModal.hide();
            
            // Show success message
            showAlert('Resource updated successfully', 'success');
        } else {
            // Show error message
            showAlert(`Error: ${data.error}`, 'danger');
        }
    })
    .catch(error => {
        console.error('Error updating resource:', error);
        showAlert('An error occurred while updating the resource', 'danger');
    });
}

// Function to show alert messages
function showAlert(message, type) {
    const alertPlaceholder = document.getElementById('alert-placeholder');
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertPlaceholder.append(wrapper);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = wrapper.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}
