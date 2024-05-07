document.getElementById("searchForm").addEventListener("submit", function(event) {
    event.preventDefault();
    var query = document.getElementById("searchInput").value.trim();
    if (query !== "") {
        fetch("/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: query })
        })
        .then(response => response.json())
        .then(data => {
            showResults(data.results);
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }
});

function showResults(results) {
    var resultsContainer = document.getElementById("resultsContainer");
    resultsContainer.innerHTML = ""; // Clear previous results
    console.log(results)
    console.log(results[0])
    if (results[0][2] == 0.0) {
            resultsContainer.textContent = "No relevant articles found."; // Display message on webpage
            return;
    }

    results.forEach(result => {
            var resultDiv = document.createElement("div");
            resultDiv.classList.add("result");

            var link = document.createElement("a");
            var score = document.createElement("div");
            link.href = result[1];
            link.textContent = result[0];
            score.textContent = result[2].toFixed(2);
            link.target = "_blank";
            resultDiv.appendChild(link);
            resultDiv.appendChild(score);


            // resultOl.appendChild(resultLi);
            resultsContainer.appendChild(resultDiv); // Append result to results container
        });
}