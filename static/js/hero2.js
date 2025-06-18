// static/js/hero2.js
$(document).ready(function(){
  // Initialize Banners Slideshow
  const $slides = $('#slides'); // Target for banners
  if ($slides.children().length > 1) { // Only initialize if there's more than one slide
    $slides.slick({
      dots: false,
      infinite: true,
      speed: 500,
      fade: true, // Or use slide effect: false
      cssEase: 'linear',
      autoplay: true,
      autoplaySpeed: 3000, // Time in milliseconds
      arrows: false, // Show next/prev arrows
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
      dots: false,
      infinite: true,
      speed: 500,
      slidesToShow: 1, // Show one slide at a time
      centerMode: true, // Makes the current slide a bit more prominent
      variableWidth: true, // Good for different image widths if any
      autoplay: true,
      autoplaySpeed: 3500,
      arrows: false,
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

  // Image expansion functionality
  $('.expandable-image-container').on('click', function() {
    const $this = $(this).find('img');
    const $lightbox = $('#lightbox');
    const $lightboxImage = $lightbox.find('img');
    if ($lightbox.length && $lightboxImage.length) {
      $lightboxImage.attr('src', $this.attr('src'));
      $lightboxImage.attr('alt', $this.attr('alt'));
      $lightbox.addClass('active');

      const $quickRemindersCard = $('.useful-cards-column').find('#card_admin_undefined'); // Target Quick Reminders card
      const $dashboardContentWrapper = $('.dashboard-content-wrapper'); // Target dashboard wrapper

      // Store original position
      $quickRemindersCard.data('original-position', $quickRemindersCard.parent());

      // Move Quick Reminders card to the top
      $quickRemindersCard.prependTo($dashboardContentWrapper);
    }
  });

  // Close lightbox
  $('#lightbox .lightbox-close').on('click', function() {
    $('#lightbox').removeClass('active');

    const $quickRemindersCard = $('.useful-cards-column').find('#card_admin_undefined'); // Target Quick Reminders card

    // Move Quick Reminders card back to its original position
    $quickRemindersCard.data('original-position').prepend($quickRemindersCard);
  });
  // Optional: Close lightbox on clicking outside the image
  $('#lightbox').on('click', function(e) {
    if ($(e.target).is('#lightbox')) {
      $('#lightbox').removeClass('active');

      const $quickRemindersCard = $('.useful-cards-column').find('#card_admin_undefined'); // Target Quick Reminders card

      // Move Quick Reminders card back to its original position
      $quickRemindersCard.data('original-position').prepend($quickRemindersCard);
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

function expandImage(element) {
  // Get the image source
  const img = element.querySelector('img');
  const src = img.src;
  const alt = img.alt;

  // Get the Quick Reminders card
  const quickRemindersCard = document.querySelector('.useful-cards-column .card:has(.card-title:has(i.fa-bell))');

  // Store the original position of the Quick Reminders card
  const originalPosition = quickRemindersCard.parentNode;
  quickRemindersCard.dataset.originalPosition = Array.prototype.indexOf.call(originalPosition.children, quickRemindersCard);

  // Move the Quick Reminders card to the top
  document.querySelector('.dashboard-content-wrapper').prepend(quickRemindersCard);

  // Create the lightbox
  const lightbox = document.createElement('div');
  lightbox.id = 'lightbox';
  lightbox.style.position = 'fixed';
  lightbox.style.top = '0';
  lightbox.style.left = '0';
  lightbox.style.width = '100%';
  lightbox.style.height = '100%';
  lightbox.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
  lightbox.style.display = 'flex';
  lightbox.style.justifyContent = 'center';
  lightbox.style.alignItems = 'center';
  lightbox.style.zIndex = '10000';

  // Create the image
  const lightboxImg = document.createElement('img');
  lightboxImg.src = src;
  lightboxImg.alt = alt;
  lightboxImg.style.maxWidth = '90vw';
  lightboxImg.style.maxHeight = '90vh';
  lightboxImg.style.objectFit = 'contain';

  // Create the close button
  const closeButton = document.createElement('span');
  closeButton.innerHTML = '&times;';
  closeButton.style.position = 'absolute';
  closeButton.style.top = '20px';
  closeButton.style.right = '30px';
  closeButton.style.color = 'white';
  closeButton.style.fontSize = '3em';
  closeButton.style.cursor = 'pointer';
  closeButton.onclick = function() {
    document.body.removeChild(lightbox);

    // Move the Quick Reminders card back to its original position
    originalPosition.insertBefore(quickRemindersCard, originalPosition.children[quickRemindersCard.dataset.originalPosition]);
  };

  // Add the image and close button to the lightbox
  lightbox.appendChild(lightboxImg);
  lightbox.appendChild(closeButton);

  // Add the lightbox to the document
  document.body.appendChild(lightbox);
}
