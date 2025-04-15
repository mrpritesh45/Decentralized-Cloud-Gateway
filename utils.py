def find_matching_resources(request, resources_db):
    """
    Find a resource that matches the request requirements.
    
    Args:
        request: A ResourceRequest object
        resources_db: Dictionary of resources
        
    Returns:
        Resource object if a match is found, None otherwise
    """
    # Filter resources that match the request type and are available
    matching_resources = [
        r for r in resources_db.values() 
        if r.resource_type == request.resource_type and 
        r.availability and 
        r.amount >= request.amount and
        r.user_id != request.user_id  # Don't allocate user's own resources
    ]
    
    if not matching_resources:
        return None
    
    # Sort by amount (to find closest match)
    matching_resources.sort(key=lambda r: r.amount)
    
    # Return the first match (smallest adequate resource)
    return matching_resources[0]

def calculate_system_stats(users_db, resources_db, resource_requests_db):
    """
    Calculate statistics for the system dashboard.
    
    Args:
        users_db: Dictionary of users
        resources_db: Dictionary of resources
        resource_requests_db: Dictionary of resource requests
        
    Returns:
        Dictionary of statistics
    """
    # Count of users, resources, requests
    user_count = len(users_db)
    resource_count = len(resources_db)
    request_count = len(resource_requests_db)
    
    # Calculate available resources by type
    available_resources = {
        'cpu': 0,
        'memory': 0,
        'storage': 0
    }
    
    for resource in resources_db.values():
        if resource.availability:
            available_resources[resource.resource_type] += resource.amount
    
    # Calculate allocated resources by type
    allocated_resources = {
        'cpu': 0,
        'memory': 0,
        'storage': 0
    }
    
    for resource in resources_db.values():
        if not resource.availability and resource.allocated_to is not None:
            allocated_resources[resource.resource_type] += resource.amount
    
    # Calculate request statistics
    pending_requests = len([r for r in resource_requests_db.values() if r.status == "pending"])
    approved_requests = len([r for r in resource_requests_db.values() if r.status == "approved"])
    completed_requests = len([r for r in resource_requests_db.values() if r.status == "completed"])
    
    # Calculate total resources by type
    total_resources = {
        'cpu': 0,
        'memory': 0,
        'storage': 0
    }
    
    for resource in resources_db.values():
        total_resources[resource.resource_type] += resource.amount
    
    # Calculate resource utilization rate
    utilization_rate = {
        'cpu': (allocated_resources['cpu'] / total_resources['cpu']) * 100 if total_resources['cpu'] > 0 else 0,
        'memory': (allocated_resources['memory'] / total_resources['memory']) * 100 if total_resources['memory'] > 0 else 0,
        'storage': (allocated_resources['storage'] / total_resources['storage']) * 100 if total_resources['storage'] > 0 else 0
    }
    
    return {
        'user_count': user_count,
        'resource_count': resource_count,
        'request_count': request_count,
        'available_resources': available_resources,
        'allocated_resources': allocated_resources,
        'total_resources': total_resources,
        'utilization_rate': utilization_rate,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'completed_requests': completed_requests
    }
