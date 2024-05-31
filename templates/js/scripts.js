function fadeOut(el) {
    el.style.opacity = 1;
    (function fade() {
        if ((el.style.opacity -= .1) < 0) {
            el.style.display = "none";
        } else {
            requestAnimationFrame(fade);
        }
    })();
};

function fadeIn(el, display) {
    el.style.opacity = 0;
    el.style.display = display || "block";
    (function fade() {
        var val = parseFloat(el.style.opacity);
        if (!((val += .1) > 1)) {
            el.style.opacity = val;
            requestAnimationFrame(fade);
        }
    })();
};

document.addEventListener("DOMContentLoaded", function() {
    
    function isPortfolioItemSelected() {
        return document.querySelector('.portfolio-item.selected') !== null;
    }

    // Function to redirect to the discussion page with appropriate action
    function redirectToDiscussionPage(action, discussionId) {
        window.location.href = `/discussions/${discussionId}/${action}`;
    }

    // Add click event listeners to portfolio items
    document.querySelectorAll('.portfolio-item').forEach(item => {
        item.addEventListener('click', function() {
            // Remove selected class from all portfolio items
            document.querySelectorAll('.portfolio-item').forEach(item => {
                item.classList.remove('selected');
            });
            // Add selected class to the clicked portfolio item
            this.classList.add('selected');
        });
    });

    // Add click event listeners to "글로 시작하기" and "말로 시작하기" buttons
    document.getElementById("text-start-button").addEventListener("click", function(event) {
        event.preventDefault(); // Prevent default action of link
        // Redirect to the discussion page with appropriate action if a portfolio item is selected
        if (isPortfolioItemSelected()) {
            const discussionId = "{{ discussion_id }}"; // discussion_id를 FastAPI 템플릿 시스템을 통해 전달받음
            redirectToDiscussionPage("text", discussionId);
        } else {
            // Show alert if no portfolio item is selected
            alert("주제를 선택하세요.");
        }
    });

    document.getElementById("voice-start-button").addEventListener("click", function(event) {
        event.preventDefault(); // Prevent default action of link
        // Redirect to the discussion page with appropriate action if a portfolio item is selected
        if (isPortfolioItemSelected()) {
            const discussionId = "{{ discussion_id }}"; // discussion_id를 FastAPI 템플릿 시스템을 통해 전달받음
            redirectToDiscussionPage("voice", discussionId);
        } else {
            // Show alert if no portfolio item is selected
            alert("주제를 선택하세요.");
        }
    });
});