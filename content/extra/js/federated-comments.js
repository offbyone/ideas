/**
 * Federated Comments System
 * Handles loading and displaying comments from the Fediverse
 */

// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function() {
  // Initialize dialog elements if they exist
  const dialog = document.querySelector('dialog.mastodon');
  const replyButton = document.getElementById('replyButton');
  const copyButton = document.getElementById('copyButton');
  const cancelButton = document.getElementById('cancelButton');
  const commentsList = document.getElementById('mastodon-comments-list');
  
  // Initialize the dialog event listeners if the dialog exists
  if (dialog) {
    if (replyButton) {
      replyButton.addEventListener('click', () => {
        dialog.showModal();
      });
    }
    
    if (copyButton) {
      copyButton.addEventListener('click', () => {
        const input = copyButton.closest('.copypaste').querySelector('input');
        const url = input.value;
        navigator.clipboard.writeText(url);
        
        // Visual feedback that the URL was copied
        const originalText = copyButton.textContent;
        copyButton.textContent = "Copied!";
        setTimeout(() => {
          copyButton.textContent = originalText;
        }, 2000);
      });
    }
    
    if (cancelButton) {
      cancelButton.addEventListener('click', () => {
        dialog.close();
      });
    }
    
    dialog.addEventListener('keydown', e => {
      if (e.key === 'Escape') dialog.close();
    });
  }
  
  // Helper function to escape HTML
  function escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
  
  // Load comments if there's a comments list element
  if (commentsList) {
    // Get the toot domain and ID from the data attributes
    const tootDomain = commentsList.getAttribute('data-domain');
    const tootId = commentsList.getAttribute('data-id');
    
    if (tootDomain && tootId) {
      commentsList.innerHTML = "Loading comments...";
      
      fetch(`https://${tootDomain}/api/v1/statuses/${tootId}/context`)
        .then(function(response) {
          return response.json();
        })
        .then(function(data) {
          if (data && 
              data['descendants'] && 
              Array.isArray(data['descendants']) && 
              data['descendants'].length > 0) {
            
            commentsList.innerHTML = "";
            
            data['descendants'].forEach(function(reply) {
              reply.account.display_name = escapeHtml(reply.account.display_name);
              
              reply.account.emojis.forEach(emoji => {
                reply.account.display_name = reply.account.display_name.replace(`:${emoji.shortcode}:`, 
                  `<img src="${escapeHtml(emoji.static_url)}" alt="Emoji ${emoji.shortcode}" height="20" width="20" />`);
              });
              
              const mastodonComment = 
                `<div class="mastodon-comment post-comment">
                  <div class="avatar">
                    <img src="${escapeHtml(reply.account.avatar_static)}" height=60 width=60 alt="">
                  </div>
                  <div class="content">
                    <div class="author">
                      <a href="${reply.account.url}" rel="nofollow">
                        <span>${reply.account.display_name}</span>
                        <span class="disabled">${escapeHtml(reply.account.acct)}</span>
                      </a>
                      <a class="date" href="${reply.uri}" rel="nofollow">
                        ${reply.created_at.substr(0, 10)}
                      </a>
                    </div>
                    <div class="mastodon-comment-content">${reply.content}</div>
                  </div>
                </div>`;
              
              // Check if DOMPurify is available
              if (typeof DOMPurify !== 'undefined') {
                commentsList.appendChild(DOMPurify.sanitize(mastodonComment, {'RETURN_DOM_FRAGMENT': true}));
              } else {
                // Fallback if DOMPurify is not available
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = mastodonComment;
                commentsList.appendChild(tempDiv.firstChild);
                console.warn('DOMPurify not available, using unsafe fallback');
              }
            });
          } else {
            commentsList.innerHTML = "<p>No comments found. I'd love to hear from you!</p>";
          }
        })
        .catch(function(error) {
          commentsList.innerHTML = "<p>Error loading comments. Please try again later.</p>";
          console.error("Error fetching comments:", error);
        });
    }
  }
});