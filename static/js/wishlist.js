// Wishlist functionality with beautiful animations
document.addEventListener('DOMContentLoaded', function() {
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const bookId = this.dataset.bookId;
            const isInWishlist = this.classList.contains('active');
            
            // Add visual feedback
            this.style.pointerEvents = 'none';
            this.style.opacity = '0.6';
            
            // Determine the action
            const action = isInWishlist ? 'remove' : 'add';
            const url = `/wishlist/${action}/${bookId}/`;
            
            // Send AJAX request
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Toggle the active state
                    this.classList.toggle('active');
                    
                    // Update the icon based on state
                    const icon = this.querySelector('i');
                    if (this.classList.contains('active')) {
                        icon.classList.remove('bi-heart');
                        icon.classList.add('bi-heart-fill');
                        this.style.color = '#ff1744';
                        
                        // Add pop animation
                        this.style.animation = 'none';
                        setTimeout(() => {
                            this.style.animation = 'heartPop 0.6s ease-out';
                        }, 10);
                    } else {
                        icon.classList.remove('bi-heart-fill');
                        icon.classList.add('bi-heart');
                        this.style.color = '';
                    }
                    
                    // Show a toast notification
                    showNotification(data.message, 'success');
                } else {
                    console.error('Error:', data.message);
                    showNotification('Xatolik yuz berdi', 'error');
                }
                
                // Re-enable button
                this.style.pointerEvents = 'auto';
                this.style.opacity = '1';
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Xatolik yuz berdi', 'error');
                this.style.pointerEvents = 'auto';
                this.style.opacity = '1';
            });
        });
        
        // Check if book is in wishlist on page load
        const bookId = button.dataset.bookId;
        fetch(`/wishlist/check/${bookId}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.is_in_wishlist) {
                button.classList.add('active');
                const icon = button.querySelector('i');
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
                button.style.color = '#ff1744';
            }
        })
        .catch(error => console.error('Error checking wishlist:', error));
    });
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Helper function to show beautiful notifications
function showNotification(message, type = 'success') {
    const alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
    
    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show notification-toast" role="alert" style="
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 450px;
            animation: slideInNotification 0.4s ease-out;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
            border: none;
            border-radius: 12px;
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <i class="bi bi-${type === 'error' ? 'exclamation-circle' : 'check-circle'}-fill" style="font-size: 1.2rem;"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    const container = document.createElement('div');
    container.innerHTML = alertHTML;
    const notification = container.firstElementChild;
    document.body.appendChild(notification);
    
    // Auto remove after 3.5 seconds
    setTimeout(() => {
        if (notification && notification.parentNode) {
            notification.style.animation = 'slideOutNotification 0.3s ease-out';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, 3500);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInNotification {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutNotification {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
    
    @keyframes heartPop {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.3);
        }
        100% {
            transform: scale(1);
        }
    }
    
    .notification-toast {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 251, 252, 0.98) 100%) !important;
        backdrop-filter: blur(10px);
    }
    
    .notification-toast.alert-success {
        border-left: 4px solid #2ecc71 !important;
    }
    
    .notification-toast.alert-danger {
        border-left: 4px solid #e74c3c !important;
    }
`;
document.head.appendChild(style);
