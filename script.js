// ============================================
// SMOOTH SCROLLING
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
// ============================================
// NAVBAR SCROLL EFFECT
// ============================================
const navbar = document.querySelector('.navbar');
const navAccent = document.querySelector('.nav-accent');
let lastScrollTop = 0;
window.addEventListener('scroll', () => {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    if (scrollTop > 100) {
        navbar.style.background = 'rgba(13, 17, 23, 0.98)';
        navbar.style.boxShadow = '0 6px 24px rgba(0, 0, 0, 0.4)';
    } else {
        navbar.style.background = 'rgba(13, 17, 23, 0.95)';
        navbar.style.boxShadow = '0 3px 12px rgba(0, 0, 0, 0.3)';
    }
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
});
// ============================================
// ANIMATE PROGRESS BARS ON SCROLL
// ============================================
const observerOptions = {
    threshold: 0.5,
    rootMargin: '0px 0px -50px 0px'
};
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.transition = 'width 1s ease-out';
        }
    });
}, observerOptions);
document.querySelectorAll('.progress-bar').forEach(bar => {
    observer.observe(bar);
});
// ============================================
// ANIMATE CARDS ON SCROLL
// ============================================
const cardObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.style.animation = `fadeInUp 0.6s ease-out forwards`;
            }, index * 100);
        }
    });
}, { threshold: 0.1 });
document.querySelectorAll('.work-card').forEach(card => {
    card.style.opacity = '0';
    cardObserver.observe(card);
});
// ============================================
// ADD FADE-IN ANIMATION
// ============================================
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
// ============================================
// INTERACTIVE BADGES
// ============================================
document.querySelectorAll('.badge').forEach(badge => {
    badge.addEventListener('mouseenter', function () {
        this.style.transform = 'scale(1.05)';
    });
    badge.addEventListener('mouseleave', function () {
        this.style.transform = 'scale(1)';
    });
});
// ============================================
// ACTIVE NAVIGATION LINK
// ============================================
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');
window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });
    navLinks.forEach(link => {
        link.style.color = 'var(--text-primary)';
        if (link.getAttribute('href').slice(1) === current) {
            link.style.color = 'var(--accent-1)';
        }
    });
});
console.log('Portfolio loaded successfully! 🚀');

