import uuid
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from forms import LoginForm, RegisterForm, ResourceForm, ResourceRequestForm
from models import User, Resource, ResourceRequest, users_db, resources_db, resource_requests_db
from utils import find_matching_resources, calculate_system_stats

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists
        user = next((user for user in users_db.values() if user.email == form.email.data), None)
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        if any(user.email == form.email.data for user in users_db.values()):
            flash('Email already registered', 'danger')
            return render_template('register.html', form=form)
        
        # Check if username already exists
        if any(user.username == form.username.data for user in users_db.values()):
            flash('Username already taken', 'danger')
            return render_template('register.html', form=form)
        
        # Generate a unique user ID
        user_id = max(users_db.keys(), default=0) + 1
        
        # Create new user
        new_user = User(
            id=user_id,
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        
        users_db[user_id] = new_user
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's shared resources
    user_resources = [r for r in resources_db.values() if r.user_id == current_user.id]
    
    # Get user's resource requests
    user_requests = [r for r in resource_requests_db.values() if r.user_id == current_user.id]
    
    # Get resources allocated to the user
    allocated_resources = [r for r in resources_db.values() if r.allocated_to == current_user.id]
    
    # Calculate system stats
    stats = calculate_system_stats(users_db, resources_db, resource_requests_db)
    
    return render_template(
        'dashboard.html',
        user=current_user,
        resources=user_resources,
        requests=user_requests,
        allocated=allocated_resources,
        stats=stats
    )

@app.route('/resource-management', methods=['GET', 'POST'])
@login_required
def resource_management():
    form = ResourceForm()
    
    if form.validate_on_submit():
        # Generate a unique resource ID
        resource_id = str(uuid.uuid4())
        
        # Create new resource
        new_resource = Resource(
            id=resource_id,
            user_id=current_user.id,
            resource_type=form.resource_type.data,
            amount=form.amount.data,
            availability=form.availability.data
        )
        
        resources_db[resource_id] = new_resource
        current_user.shared_resources.append(resource_id)
        
        flash('Resource added successfully!', 'success')
        return redirect(url_for('resource_management'))
    
    # Get user's shared resources
    user_resources = [r for r in resources_db.values() if r.user_id == current_user.id]
    
    return render_template(
        'resource_management.html',
        form=form,
        resources=user_resources
    )

@app.route('/resource-requests', methods=['GET', 'POST'])
@login_required
def resource_requests():
    form = ResourceRequestForm()
    
    if form.validate_on_submit():
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Create new resource request
        new_request = ResourceRequest(
            id=request_id,
            user_id=current_user.id,
            resource_type=form.resource_type.data,
            amount=form.amount.data,
            duration=form.duration.data if form.duration.data else None
        )
        
        resource_requests_db[request_id] = new_request
        current_user.resource_requests.append(request_id)
        
        # Try to find matching resources
        matched_resource = find_matching_resources(new_request, resources_db)
        
        if matched_resource:
            # Allocate the resource to the user
            matched_resource.allocate(current_user.id)
            new_request.approve(matched_resource.id)
            current_user.allocated_resources.append(matched_resource.id)
            flash('Resource request approved and resource allocated!', 'success')
        else:
            flash('Resource request submitted. No matching resources found at the moment.', 'info')
        
        return redirect(url_for('resource_requests'))
    
    # Get user's resource requests
    user_requests = [r for r in resource_requests_db.values() if r.user_id == current_user.id]
    
    # Get resources allocated to the user
    allocated_resources = [r for r in resources_db.values() if r.allocated_to == current_user.id]
    
    # Get available resources in the system
    available_resources = [r for r in resources_db.values() if r.availability and r.user_id != current_user.id]
    
    # Calculate system stats - needed for the template
    stats = calculate_system_stats(users_db, resources_db, resource_requests_db)
    
    return render_template(
        'resource_requests.html',
        form=form,
        requests=user_requests,
        allocated=allocated_resources,
        available=available_resources,
        stats=stats
    )

@app.route('/api/resources')
@login_required
def api_resources():
    # Get all resources for visualization
    all_resources = [r.to_dict() for r in resources_db.values()]
    return jsonify(all_resources)

@app.route('/api/update-resource/<resource_id>', methods=['POST'])
@login_required
def update_resource(resource_id):
    resource = resources_db.get(resource_id)
    
    if not resource:
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    
    if resource.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    data = request.json
    
    resource.update(
        resource_type=data.get('resource_type', resource.resource_type),
        amount=data.get('amount', resource.amount),
        availability=data.get('availability', resource.availability)
    )
    
    return jsonify({'success': True, 'resource': resource.to_dict()})

@app.route('/api/delete-resource/<resource_id>', methods=['POST'])
@login_required
def delete_resource(resource_id):
    resource = resources_db.get(resource_id)
    
    if not resource:
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    
    if resource.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Check if resource is allocated
    if resource.allocated_to:
        return jsonify({'success': False, 'error': 'Cannot delete allocated resource'}), 400
    
    # Remove resource from user's shared resources
    if resource_id in current_user.shared_resources:
        current_user.shared_resources.remove(resource_id)
    
    # Remove resource from database
    del resources_db[resource_id]
    
    return jsonify({'success': True})

@app.route('/api/cancel-request/<request_id>', methods=['POST'])
@login_required
def cancel_request(request_id):
    req = resource_requests_db.get(request_id)
    
    if not req:
        return jsonify({'success': False, 'error': 'Request not found'}), 404
    
    if req.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Check if request has an allocated resource
    if req.status == "approved" and req.allocated_resource_id:
        resource = resources_db.get(req.allocated_resource_id)
        if resource:
            resource.deallocate()
            
            # Remove from user's allocated resources
            if req.allocated_resource_id in current_user.allocated_resources:
                current_user.allocated_resources.remove(req.allocated_resource_id)
    
    # Remove request from database
    del resource_requests_db[request_id]
    
    # Remove from user's requests
    if request_id in current_user.resource_requests:
        current_user.resource_requests.remove(request_id)
    
    return jsonify({'success': True})

@app.route('/api/release-resource/<resource_id>', methods=['POST'])
@login_required
def release_resource(resource_id):
    resource = resources_db.get(resource_id)
    
    if not resource:
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    
    if resource.allocated_to != current_user.id:
        return jsonify({'success': False, 'error': 'Resource not allocated to you'}), 403
    
    # Find the request that allocated this resource
    request_id = None
    for req_id, req in resource_requests_db.items():
        if req.allocated_resource_id == resource_id and req.user_id == current_user.id:
            request_id = req_id
            break
    
    # Mark the request as completed
    if request_id and request_id in resource_requests_db:
        resource_requests_db[request_id].complete()
    
    # Deallocate the resource
    resource.deallocate()
    
    # Remove from user's allocated resources
    if resource_id in current_user.allocated_resources:
        current_user.allocated_resources.remove(resource_id)
    
    return jsonify({'success': True})

@app.route('/api/stats')
@login_required
def api_stats():
    stats = calculate_system_stats(users_db, resources_db, resource_requests_db)
    return jsonify(stats)
