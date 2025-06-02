document.addEventListener('DOMContentLoaded', function() {
  // Slick Carousel Initialization
  $('#slides').slick({
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
    arrows: false
  });

  $('#slides2').slick({
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
    arrows: false
  });

  // Lightbox Functionality
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = lightbox.querySelector('img');
  const lightboxClose = document.querySelector('.lightbox-close');
  const lightboxPrev = document.querySelector('.lightbox-prev');
  const lightboxNext = document.querySelector('.lightbox-next');
  let currentIndex = 0;
  let images = [];

  function openLightbox(index) {
    currentIndex = index;
    lightboxImg.src = images[currentIndex];
    lightbox.classList.add('active');
    updateLightboxControls();
  }

  function closeLightbox() {
    lightbox.classList.remove('active');
  }

  function updateLightboxControls() {
    lightboxPrev.style.display = currentIndex > 0 ? 'block' : 'none';
    lightboxNext.style.display = currentIndex < images.length - 1 ? 'block' : 'none';
  }

  function changeImage(direction) {
    currentIndex += direction;
    lightboxImg.src = images[currentIndex];
    updateLightboxControls();
  }

  document.querySelectorAll('.slides img').forEach((img, index) => {
    images.push(img.src);
    img.addEventListener('click', () => openLightbox(index));
  });

  lightboxClose.addEventListener('click', closeLightbox);
  lightboxPrev.addEventListener('click', () => changeImage(-1));
  lightboxNext.addEventListener('click', () => changeImage(1));

  // Gift Animation
  const giftOverlay = document.querySelector('.gift-overlay');
  const giftContainer = document.querySelector('.gift-container');
  const giftBox = document.querySelector('.gift-box');
  const giftLid = document.querySelector('.gift-lid');
  const wishesText = document.querySelector('.wishes-text');
  const sparkles = document.querySelector('.sparkles');
  const closeBtn = document.querySelector('.close-btn');

  function openGift() {
    giftLid.classList.add('opened');
    wishesText.classList.add('opened');
    sparkles.classList.add('opened');
    giftContainer.classList.add('balloon-mode');
    setTimeout(() => {
      giftContainer.classList.remove('balloon-mode');
      giftContainer.classList.add('falling-mode');
    }, 3000);
  }

  function closeGift() {
    giftOverlay.style.display = 'none';
    giftLid.classList.remove('opened');
    wishesText.classList.remove('opened');
    sparkles.classList.remove('opened');
    giftContainer.classList.remove('falling-mode');
  }

  giftBox.addEventListener('click', openGift);
  closeBtn.addEventListener('click', closeGift);

  // Weather Buttons
  const weatherButtons = document.querySelectorAll('.weather-buttons button');
  weatherButtons.forEach(button => {
    button.addEventListener('click', function() {
      weatherButtons.forEach(btn => btn.classList.remove('active'));
      this.classList.add('active');
    });
  });
});

    // Unrelated functions from original code
    function changeWeather(weather, videoSource) {
      const video = document.querySelector('.background-video');
      video.src = videoSource;
      video.load();
      video.play();
    }

    function openGift() {
      // Ensure 'giftOverlay' element exists in your HTML if you use this
      const giftOverlay = document.getElementById("giftOverlay");
      if (giftOverlay) giftOverlay.classList.add('opened');
    }

    function closeGift() {
      // Ensure 'giftOverlay' element exists in your HTML if you use this
      const giftOverlay = document.getElementById("giftOverlay");
      if (giftOverlay) giftOverlay.classList.remove('opened');
    }

    // Store image sources for each gallery
    let gallerySources = {
        'slides': [],
        'slides2': []
    };

    // Global for lightbox state
    let currentLightboxGalleryId = null;
    let currentLightboxImageIndex = 0;

    function openLightbox(event, galleryId) {
        const lightbox = document.getElementById("lightbox");
        if (!lightbox) return;
        const lightboxImg = lightbox.querySelector('img');
        if (!lightboxImg) return;
        
        const clickedImgSrc = event.target.src;

        currentLightboxGalleryId = galleryId;
        let imagesForCurrentGallery = gallerySources[galleryId];

        // Fallback to populate if gallerySources was not populated or is empty for this gallery
        if (!imagesForCurrentGallery || imagesForCurrentGallery.length === 0) {
            const slideContainer = document.getElementById(galleryId);
            if (slideContainer) {
                const uniqueImageSources = [];
                const seenSources = new Set();
                // Query images from slick slides, excluding clones
                const imageElements = slideContainer.querySelectorAll('.slick-slide:not(.slick-cloned) img');
                imageElements.forEach(img => {
                    if (img.src && !seenSources.has(img.src)) {
                        uniqueImageSources.push(img.src);
                        seenSources.add(img.src);
                    }
                });
                gallerySources[galleryId] = uniqueImageSources; // Cache it
                imagesForCurrentGallery = uniqueImageSources;
            }
        }
        
        if (!imagesForCurrentGallery || imagesForCurrentGallery.length === 0) {
            console.error("Lightbox: No images to display for gallery: " + galleryId);
            return;
        }

        currentLightboxImageIndex = imagesForCurrentGallery.findIndex(src => src === clickedImgSrc);
        
        if (currentLightboxImageIndex === -1) {
             // Fallback: if exact src match fails (e.g. due to relative vs absolute path issues after slick init)
             // try to find based on the original index if possible, or default to first image.
             // This example defaults to 0 if not found. A more robust solution might involve data attributes on images.
            const slickSlide = event.target.closest('.slick-slide:not(.slick-cloned)');
            if (slickSlide && slickSlide.dataset.slickIndex) {
                 let slickIndex = parseInt(slickSlide.dataset.slickIndex);
                 if(slickIndex >=0 && slickIndex < imagesForCurrentGallery.length){
                    currentLightboxImageIndex = slickIndex;
                 } else {
                    currentLightboxImageIndex = 0;
                 }
            } else {
                 currentLightboxImageIndex = 0; // Default to first image
            }
        }

        lightboxImg.src = imagesForCurrentGallery[currentLightboxImageIndex];
        lightbox.classList.add('active');
        updateLightboxNavButtons(imagesForCurrentGallery.length);
    }

    function closeLightbox() {
        const lightbox = document.getElementById("lightbox");
        if (lightbox) lightbox.classList.remove('active');
        currentLightboxGalleryId = null; // Reset gallery ID
    }

    function changeLightboxSlide(n) {
        if (!currentLightboxGalleryId) return;

        const imagesForCurrentGallery = gallerySources[currentLightboxGalleryId];
        if (!imagesForCurrentGallery || imagesForCurrentGallery.length === 0) return;

        currentLightboxImageIndex = (currentLightboxImageIndex + n + imagesForCurrentGallery.length) % imagesForCurrentGallery.length;
        const lightboxImg = document.querySelector('.lightbox img');
        if (lightboxImg) lightboxImg.src = imagesForCurrentGallery[currentLightboxImageIndex];
    }

    function updateLightboxNavButtons(numImages) {
        const prevButton = document.querySelector('.lightbox-prev');
        const nextButton = document.querySelector('.lightbox-next');
        if (!prevButton || !nextButton) return;

        if (numImages <= 1) {
            prevButton.style.display = 'none';
            nextButton.style.display = 'none';
        } else {
            prevButton.style.display = 'block';
            nextButton.style.display = 'block';
        }
    }

    $(document).ready(function(){
      // Initialize Slick Carousel for #slides
      if ($('#slides').length > 0 && $('#slides img').length > 0) {
        $('#slides').slick({
            dots: true,
            infinite: true,
            speed: 500,
            fade: true,
            cssEase: 'linear',
            autoplay: true,
            autoplaySpeed: 3000,
            adaptiveHeight: true
        });
      }

      // Initialize Slick Carousel for #slides2
      if ($('#slides2').length > 0 && $('#slides2 img').length > 0) {
        $('#slides2').slick({
            dots: true,
            infinite: true,
            speed: 500,
            //fade: true, // You can choose different effects for different sliders
            //cssEase: 'linear',
            autoplay: true,
            autoplaySpeed: 3500,
            adaptiveHeight: true
        });
      }

      // Populate gallerySources AFTER Slick has initialized
      // This ensures we get sources from the actual slides Slick is using (excluding clones)
      // and that their src attributes are fully resolved.
      function populateGallerySource(galleryId) {
            const slideContainer = $('#' + galleryId);
            if (slideContainer.length > 0 && slideContainer.hasClass('slick-initialized')) {
                const uniqueImageSources = [];
                const seenSources = new Set();
                slideContainer.find('.slick-slide:not(.slick-cloned) img').each(function() {
                    const imgSrc = $(this).attr('src');
                    if (imgSrc && !seenSources.has(imgSrc)) {
                        uniqueImageSources.push(imgSrc);
                        seenSources.add(imgSrc);
                    }
                });
                gallerySources[galleryId] = uniqueImageSources;
            } else if (slideContainer.length > 0) { // Fallback for non-slick or pre-slick
                 gallerySources[galleryId] = Array.from(document.querySelectorAll('#' + galleryId + ' img')).map(img => img.src);
                 gallerySources[galleryId] = [...new Set(gallerySources[galleryId])]; // Ensure unique
            }
      }
      
      populateGallerySource('slides');
      populateGallerySource('slides2');


      // Event Listeners for opening lightbox from slideshows
      const slideshowContainer1 = document.getElementById('slideshowContainerElement');
      if (slideshowContainer1) {
          slideshowContainer1.addEventListener('click', function(event) {
              if (event.target.tagName === 'IMG' && $(event.target).closest('.slick-slider').length) { // Ensure click is on an image within a slick slider
                  openLightbox(event, 'slides');
              }
          });
      }

      const slideshowContainer2 = document.getElementById('slideshowContainerElement2');
      if (slideshowContainer2) {
          slideshowContainer2.addEventListener('click', function(event) {
              if (event.target.tagName === 'IMG' && $(event.target).closest('.slick-slider').length) {
                  openLightbox(event, 'slides2');
              }
          });
      }

      // Lightbox controls (already assigned via inline onclick, but this is an alternative)
      // document.querySelector('.lightbox-close').onclick = closeLightbox;
    });
