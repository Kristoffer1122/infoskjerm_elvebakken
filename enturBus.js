let DeparturesData = null;

async function FetchDepartures() {
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
                            destinationDisplay { frontText }
                            serviceJourney {
                                journeyPattern {
                                    line { id transportMode }
                                }
                            }
                        }
                    }
                }
                `,
			}),
		});
		if (!response.ok) throw new Error(`Response ${response.status}`);
		DeparturesData = await response.json();
		ShowDepartures();
	} catch (error) {
		console.error("Fetch error:", error.message);
	}
}

function ShowDepartures() {
	if (!DeparturesData || !DeparturesData.data || !DeparturesData.data.stopPlace) {
		document.getElementById("departures").innerHTML = "<span>Ingen avganger</span>";
		return;
	}

	// Grouping for each direction
	const Sentrum = ["Kværnerbyen", "Ekeberg hageby"];
	const Vest = ["Kjelsås stasjon", "Tåsen"];

	const Calls = DeparturesData.data.stopPlace.estimatedCalls;
	const SentrumDepartures = [];
	const VestDepartures = [];

	for (let Call of Calls) {
		const Destination = Call.destinationDisplay.frontText;
		if (Sentrum.includes(Destination)) {
			SentrumDepartures.push(Call);
		} else if (Vest.includes(Destination)) {
			VestDepartures.push(Call);
		}
	}

	// Render vertically: Sentrum row above, Vest row below
	const Container = document.getElementById("departures");
	Container.innerHTML = `
        <div class="departures-row" id="sentrum-row">
            <div class="direction-header">Retning Sentrum</div>
            <div class="departures-list" id="sentrum-list"></div>
        </div>
        <div class="departures-row" id="vest-row">
            <div class="direction-header">Retning Vest</div>
            <div class="departures-list" id="vest-list"></div>
        </div>
    `;

	// Helper to render a bus departure
	function renderDeparture(Call) {
		const ExpectedArrival = new Date(Call.expectedArrivalTime);
		const Now = new Date();
		const TimeDiff = Math.floor((ExpectedArrival - Now) / 1000 / 60);
		const Destination = Call.destinationDisplay.frontText;
		const LineId = Call.serviceJourney.journeyPattern.line.id.split(":").pop();
		const Div = document.createElement("div");
		Div.classList.add("departure");
		Div.innerHTML = `
            <span class="bus-line">${LineId}</span>
            <span class="bus-direction">${Destination}</span>
            <span class="bus-time">${TimeDiff <= 0 ? "nå" : TimeDiff + " min"}</span>
        `;
		return Div;
	}

	// Populate Sentrum row
	const SentrumList = Container.querySelector("#sentrum-list");
	if (SentrumDepartures.length > 0) {
		SentrumDepartures.forEach(Call => {
			SentrumList.appendChild(renderDeparture(Call));
		});
	} else {
		const Empty = document.createElement("div");
		Empty.className = "empty-message";
		Empty.textContent = "Ingen avganger";
		SentrumList.appendChild(Empty);
	}

	// Populate Vest row
	const VestList = Container.querySelector("#vest-list");
	if (VestDepartures.length > 0) {
		VestDepartures.forEach(Call => {
			VestList.appendChild(renderDeparture(Call));
		});
	} else {
		const Empty = document.createElement("div");
		Empty.className = "empty-message";
		Empty.textContent = "Ingen avganger";
		VestList.appendChild(Empty);
	}
}

// Initial and periodic updates every 30 seconds
setInterval(FetchDepartures, 30000);
FetchDepartures();
