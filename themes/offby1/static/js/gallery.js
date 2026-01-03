// Initialize Magnific Popup for image galleries
document.addEventListener('DOMContentLoaded', function() {
  // Find sections with gallery-related IDs or classes
  // Look for: id="gallery", id contains "gallery", or class="gallery"
  const gallerySections = document.querySelectorAll('section[id*="gallery"], section.gallery');
  
  gallerySections.forEach((gallerySection) => {
    // Find all figures within the gallery section
    const galleryFigures = gallerySection.querySelectorAll('figure.align-default');
    
    if (galleryFigures.length > 0) {
      // Wrap gallery images in links for lightbox
      galleryFigures.forEach((figure) => {
        const img = figure.querySelector('img');
        if (img && !img.closest('a')) {
          const link = document.createElement('a');
          link.href = img.src;
          link.className = 'gallery-image';
          link.setAttribute('data-gallery', 'main');
          
          // Get caption text if it exists
          const caption = figure.querySelector('.caption-text');
          if (caption) {
            link.title = caption.textContent.trim();
          }
          
          // Wrap the image in the link
          img.parentNode.insertBefore(link, img);
          link.appendChild(img);
        }
      });
    }
  });
  
  // Initialize Magnific Popup on manually created gallery images
  if (document.querySelectorAll('.gallery-image').length > 0) {
    jQuery('.gallery-image').magnificPopup({
      type: 'image',
      gallery: {
        enabled: true,
        navigateByImgClick: true,
        preload: [0, 1]
      },
      image: {
        titleSrc: 'title'
      }
    });
  }
  
  // Initialize Magnific Popup for photos plugin galleries
  // These are already created by the pelican photos plugin
  if (document.querySelectorAll('.gallery-item').length > 0) {
    jQuery('.gallery-item').magnificPopup({
      type: 'image',
      gallery: {
        enabled: true,
        navigateByImgClick: true,
        preload: [0, 1]
      },
      image: {
        titleSrc: function(item) {
          // Use data-caption if available, otherwise use title attribute
          const caption = item.el.attr('data-caption');
          const exif = item.el.attr('data-exif');
          let title = caption || item.el.attr('title') || '';
          
          // Add EXIF data as an expandable details section if available
          if (exif && exif !== 'None') {
            title += '<details class="mfp-exif-details"><summary>Photo details</summary><small>' + exif + '</small></details>';
          }
          
          return title;
        },
        markup: '<div class="mfp-figure">' +
                  '<div class="mfp-close"></div>' +
                  '<div class="mfp-img"></div>' +
                  '<div class="mfp-bottom-bar">' +
                    '<div class="mfp-title"></div>' +
                    '<div class="mfp-counter"></div>' +
                  '</div>' +
                '</div>'
      },
      callbacks: {
        markupParse: function(template, values, item) {
          // Manually set the title HTML to avoid escaping
          if (values.title) {
            setTimeout(() => {
              template.find('.mfp-title').html(values.title);
            }, 0);
          }
        }
      }
    });
  }
});
