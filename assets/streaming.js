window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside = window.dash_clientside.clientside || {};

/**
 * Updates the streaming content in the chat area
 * 
 * @param {string} streamData - JSON string containing streaming data
 * @param {number} messageId - ID of the current message being streamed
 * @returns {boolean|undefined} - Returns true to disable interval when complete, or no_update
 */
window.dash_clientside.clientside.updateStreamingContent = function(streamData, messageId) {
    if (!streamData) return window.dash_clientside.no_update;
    
    try {
        const data = JSON.parse(streamData);
        const contentElement = document.getElementById(`streaming-content-${messageId}`);
        
        if (contentElement && data.content) {
            // Update the content with the streamed text
            contentElement.textContent = data.content;
            
            // Scroll to the bottom of the chat area to show the latest content
            const chatArea = document.querySelector('.chat-area') || 
                             document.getElementById('chat-area').parentElement;
            if (chatArea) {
                chatArea.scrollTop = chatArea.scrollHeight;
            }
        }
        
        // If streaming is complete, disable the interval
        if (data.status === 'complete') {
            return true;
        }
    } catch (error) {
        console.error('Error updating streaming content:', error);
    }
    
    return window.dash_clientside.no_update;
};
