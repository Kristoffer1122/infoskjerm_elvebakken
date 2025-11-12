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

    if (!response.ok) {
      throw new Error(`Response ${response.status}`);
    }

    departuresData = await response.json();
    showDepartures()
    // console.dir(departuresData.data.stopPlace, { depth: null });
  } catch (error) {
    console.error("Fetch error:", error.message);
  }
}



setInterval(fetchDepartures, 30000);
fetchDepartures()

function showDepartures() {

  let sentrumDepartures = []
  let otherWayDepartures = []

  const sentrum = ["Kværnerbyen", "Ekeberg hageby"]
  const otherWay = ["Kjelsås stasjon", "Tåsen"]

  const calls = departuresData.data.stopPlace.estimatedCalls

  const containerOtherWay = document.getElementById("departuresOtherWay");
  const containerSentrum = document.getElementById("departuresSentrum")

  containerOtherWay.innerHTML = "";
  containerSentrum.innerHTML = "";

  //ts pmo
  for (let call of calls) {
    frontText = call.destinationDisplay.frontText
    if (sentrum.includes(frontText)) {
      sentrumDepartures.push(call)
    } else if (otherWay.includes(frontText)){
      otherWayDepartures.push(call)
    }
  }

  for (let sentrumDeparture of sentrumDepartures) {
    let sentrumFrontText = sentrumDeparture.destinationDisplay.frontText
    let sentrumLineId = sentrumDeparture.serviceJourney.journeyPattern.line.id.split(":").pop()
    let sentrumExpectedArrival = new Date(sentrumDeparture.expectedArrivalTime)
    let now = new Date()
    let sentrumTimeDiff = Math.floor((sentrumExpectedArrival - now ) / 1000 / 60)

    const sentrumDiv = document.createElement("div");
    sentrumDiv.classList.add("departures");
    sentrumDiv.innerHTML = `
      <span class="sentrumLine">${sentrumLineId} ${sentrumFrontText}</span>
      <span class="time">${sentrumTimeDiff <= 0 ? "nå" : sentrumTimeDiff + " min"}</span>
    `;
    containerSentrum.appendChild(sentrumDiv);
  }

  for (let otherWayDeparture of otherWayDepartures) {
    let otherWayFrontText = otherWayDeparture.destinationDisplay.frontText
    let otherWaylineId = otherWayDeparture.serviceJourney.journeyPattern.line.id.split(":").pop()
    let otherWayExpectedArrival = new Date(otherWayDeparture.expectedArrivalTime)
    now = new Date()
    let otherWayTimeDiff = Math.floor((otherWayExpectedArrival - now) / 1000 / 60 )

    const otherWayDiv = document.createElement("div");
    otherWayDiv.classList.add("departures");
    otherWayDiv.innerHTML = `
      <span class="otherWayLine">${otherWaylineId} ${otherWayFrontText}</span>
      <span class="time">${otherWayTimeDiff <= 0 ? "nå" : otherWayTimeDiff + " min" }</span>
    `;
    containerOtherWay.appendChild(otherWayDiv)
  }
}

setInterval(showDepartures, 9000);


