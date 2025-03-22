// Testimonial Slider
document.addEventListener('DOMContentLoaded', function() {
    const track = document.querySelector('.testimonial-track');
    const dots = document.querySelectorAll('.dot');
    let currentIndex = 0;
    
    // Set up slider
    if (track && dots.length > 0) {
        // Click event for dots
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                currentIndex = index;
                updateSlider();
            });
        });
        
        // Function to update slider position
        function updateSlider() {
            track.style.transform = `translateX(-${currentIndex * 100}%)`;
            
            // Update active dot
            dots.forEach((dot, index) => {
                if (index === currentIndex) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });
        }
        
        // Auto-rotate every 5 seconds
        setInterval(() => {
            currentIndex = (currentIndex + 1) % dots.length;
            updateSlider();
        }, 5000);
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            if (this.getAttribute('href') !== '#') {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Animation for chat messages
    function animateChat() {
        const messages = document.querySelectorAll('.message');
        messages.forEach((message, index) => {
            setTimeout(() => {
                message.style.opacity = '1';
                message.style.transform = 'translateY(0)';
            }, index * 1000);
        });
        
        // Show typing animation after all messages
        if (messages.length > 0) {
            const typingAnimation = document.querySelector('.typing-animation');
            if (typingAnimation) {
                setTimeout(() => {
                    typingAnimation.style.display = 'flex';
                }, messages.length * 1000);
            }
        }
    }
    
    // Launch Streamlit function can be called from button clicks
    window.launchStreamlit = function() {
        fetch('/run-streamlit', {method:'POST'})
            .then(response => response.text())
            .then(url => {
                window.location.href = url;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to launch Streamlit app. Please try again.');
            });
    };
    
    // Run animations on page load
    animateChat();
});