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
  
  // Initialize Magnific Popup on all gallery images (do this once after processing all sections)
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
});
