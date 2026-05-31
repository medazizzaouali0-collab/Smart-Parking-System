document.addEventListener("DOMContentLoaded", () => {
    const row1Container = document.getElementById("row-1-spots");
    const row2Container = document.getElementById("row-2-spots");

    function initGrid() {
        for(let i = 1; i <= 9; i++) {
            row1Container.innerHTML += `<div class="spot" id="spot-${i}">P${i}<span>...</span></div>`;
        }
        for(let i = 10; i <= 15; i++) {
            row2Container.innerHTML += `<div class="spot" id="spot-${i}">P${i}<span>...</span></div>`;
        }
    }

    async function updateDashboard() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            // Update Counters
            document.getElementById("total-free").innerText = data.total_free;
            document.getElementById("row1-free").innerText = data.row1_free;
            document.getElementById("row2-free").innerText = data.row2_free;

            // Update individual spots
            for (const [id, isOccupied] of Object.entries(data.spots)) {
                const spotDiv = document.getElementById(`spot-${id}`);
                if (spotDiv) {
                    if (isOccupied) {
                        spotDiv.className = "spot occupied";
                        spotDiv.querySelector("span").innerText = "OCCUPIED";
                    } else {
                        spotDiv.className = "spot free";
                        spotDiv.querySelector("span").innerText = "FREE";
                    }
                }
            }
        } catch (error) {
            console.error("Error fetching parking data:", error);
        }
    }

    initGrid();
    // Poll the backend every 1 second (1000ms)
    setInterval(updateDashboard, 1000);
});