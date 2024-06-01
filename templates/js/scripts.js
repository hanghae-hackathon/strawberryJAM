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
    function getSelectedTopicId() {
        const selectedElement = document.querySelector('.portfolio-item.selected');
        const topicId = selectedElement ? selectedElement.getAttribute('data-id') : null;
        console.log("Selected Topic ID:", topicId); // topic_id 출력
        return topicId;
    }

    async function startDiscussion(action) {
        const topicId = getSelectedTopicId();
        if (!topicId) {
            alert("주제를 선택하세요.");
            return;
        }

        // Try to parse topicId as UUID
        console.log("UUID 형식 검사 중:", topicId); // UUID 형식 검사 전 topic_id 출력
        const uuidRegex = /^[0-9a-fA-F]{32}$/; // UUID 문자열 검증
        if (!uuidRegex.test(topicId)) {
            alert("잘못된 주제 ID입니다.");
            return;
        }

        try {
            console.log("POST 요청 전송 중:", topicId); // POST 요청 전 topic_id 출력
            const response = await fetch('/discussions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic_id: topicId })
            });

            if (response.ok) {
                const data = await response.json();
                window.location.href = `/discussions/${data.id}`;
            } else {
                const errorData = await response.json();
                console.error('Error:', errorData);
                alert("토론 생성에 실패했습니다. 오류: " + errorData.detail);
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert("토론 생성 중 오류가 발생했습니다.");
        }
    }

    document.getElementById("text-start-button").addEventListener("click", function() {
        startDiscussion("text");
    });

    document.getElementById("voice-start-button").addEventListener("click", function() {
        startDiscussion("voice");
    });

    document.querySelectorAll('.portfolio-item').forEach(item => {
        item.addEventListener('click', function() {
            document.querySelectorAll('.portfolio-item').forEach(item => item.classList.remove('selected'));
            this.classList.add('selected');
        });
    });

    document.getElementById("refresh-button").addEventListener("click", function() {
        window.location.reload();
    });
});
