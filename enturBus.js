async function fetchDepartures() {
  const url = "https://api.entur.io/journey-planner/v3/graphql";

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "ET-Client-Name": "Infoboard-app",
      },
      body: JSON.stringify({
        query: `
          {
            stopPlace(id: "NSR:StopPlace:6435") {
              id
              name
              estimatedCalls(timeRange: 72100, numberOfDepartures: 12) {
                realtime
                aimedArrivalTime
                expectedArrivalTime
                destinationDisplay {
                  frontText
                }
                serviceJourney {
                  journeyPattern {
                    line {
                      id
                      transportMode
                    }
                  }
                }
              }
            }
          }
        `,
      }),
    });

    if (!response.ok) throw new Error(`Response ${response.status}`);

    departuresData = await response.json();
    showDepartures();
  } catch (error) {
    console.error("Fetch error:", error.message);
  }
}

function formatDepartureTime(expectedArrival) {
  const now = new Date();
  const timeDiff = Math.floor((expectedArrival - now) / 1000 / 60);

  if (timeDiff <= 0) return "Nå";
  if (timeDiff <= 15) return timeDiff + " min";

  return expectedArrival.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function showDepartures() {
  const sentrum = ["Kværnerbyen", "Ekeberg hageby"];
  const otherWay = ["Kjelsås stasjon", "Tåsen"];

  const calls = departuresData.data?.stopPlace?.estimatedCalls || [];
  const containerSentrum = document.getElementById("departuresSentrum");
  const containerOtherWay = document.getElementById("departuresOtherWay");

  containerSentrum.innerHTML = "";
  containerOtherWay.innerHTML = "";

  for (let call of calls) {
    const frontText = call.destinationDisplay.frontText;
    const lineId = call.serviceJourney.journeyPattern.line.id.split(":").pop();
    const expectedArrival = new Date(call.expectedArrivalTime);

    const div = document.createElement("div");
    div.classList.add("departures");
    div.innerHTML = `
      <div class="lineBox">
        <span class="lineNumber">${lineId}</span>
        <span class="lineName">${frontText}</span>
      </div>
      <span class="departureTime">${formatDepartureTime(expectedArrival)}</span>
    `;

    if (sentrum.includes(frontText)) containerSentrum.appendChild(div);
    else if (otherWay.includes(frontText)) containerOtherWay.appendChild(div);
  }
}

setInterval(fetchDepartures, 30000);
fetchDepartures();
setInterval(showDepartures, 9000);
