let slideIndex = 0;
function showSlides() {
    let slides = document.querySelectorAll('.carousel-item');
    slides.forEach((slide, index) => {
        slide.style.display = 'none';  
    });
    slideIndex++;
    if (slideIndex > slides.length) {slideIndex = 1}    
    slides[slideIndex-1].style.display = 'block';  
    setTimeout(showSlides, 2000); // Change image every 2 seconds
}

function moveSlide(step) {
    showSlides(slideIndex += step);
}

// Initialize carousel
showSlides();
