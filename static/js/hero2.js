// static/js/hero2.js
$(document).ready(function(){
  // Initialize Banners Slideshow
  const $slides = $('#slides'); // Target for banners
  if ($slides.children().length > 1) { // Only initialize if there's more than one slide
    $slides.slick({
      dots: true,
      infinite: true,
      speed: 500,
      fade: true, // Or use slide effect: false
      cssEase: 'linear',
      autoplay: true,
      autoplaySpeed: 3000, // Time in milliseconds
      arrows: true, // Show next/prev arrows
      pauseOnHover: true
    });
  } else if ($slides.children().length === 1) {
    // If only one slide, no need for carousel, but ensure it's visible
    $slides.addClass('single-slide-visible'); // You can add CSS for this class if needed
  }

  // Initialize In-House Photo Gallery Slideshow
  const $slides2 = $('#slides2'); // Target for gallery photos
  if ($slides2.children().length > 1) { // Only initialize if there's more than one slide
    $slides2.slick({
      dots: true,
      infinite: true,
      speed: 500,
      slidesToShow: 1, // Show one slide at a time
      centerMode: true, // Makes the current slide a bit more prominent
      variableWidth: true, // Good for different image widths if any
      autoplay: true,
      autoplaySpeed: 3500,
      arrows: true,
      pauseOnHover: true
      // adaptiveHeight: true // Useful if images have different heights
    });
  } else if ($slides2.children().length === 1) {
    $slides2.addClass('single-slide-visible');
  }

  // Lightbox functionality (basic example if you are using one)
  // This part depends on how your lightbox HTML is structured.
  // The example below assumes you click an image within a slide to open it in a lightbox.
  // This is a conceptual example - your actual lightbox implementation might differ.

  // If your images inside the slideshow are what trigger the lightbox:
  $('.slides figure img').on('click', function() {
    const $lightbox = $('#lightbox');
    const $lightboxImage = $lightbox.find('img');
    if ($lightbox.length && $lightboxImage.length) {
      $lightboxImage.attr('src', $(this).attr('src'));
      $lightbox.fadeIn();
    }
  });

  // Close lightbox
  $('#lightbox .lightbox-close').on('click', function() {
    $('#lightbox').fadeOut();
  });
  // Optional: Close lightbox on clicking outside the image
  $('#lightbox').on('click', function(e) {
    if ($(e.target).is('#lightbox')) { // Check if click is on the lightbox background itself
      $(this).fadeOut();
    }
  });

});

// Functions for your lightbox next/prev if you have them globally (as in your HTML)
// These would need to know the context of which slideshow is active for the lightbox
// This part is more complex and depends on your specific lightbox design.
// For now, let's assume the click on image opens it, and close works.
function closeLightbox() {
  $('#lightbox').fadeOut();
}

// The changeLightboxSlide functions would need more logic to cycle through
// the images of the currently open slideshow. This is non-trivial if you want
// it to work seamlessly with Slick's current slide.
// A simpler lightbox might just show the clicked image without slideshow controls.
// function changeLightboxSlide(direction) {
//   console.log("Lightbox slide change attempt: ", direction);
//   // Add logic here to find next/prev image related to the one currently in lightbox
// }
