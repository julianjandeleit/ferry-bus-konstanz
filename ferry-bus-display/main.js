import init, { fetch_ferries } from "./pkg/ferry_bus_wasm.js";

async function render() {
    await init();

    const data = await fetch_ferries("Allmannsdorf, Konstanz", "Kirche, Meersburg");

    const container = document.getElementById("ferry-table");
    container.innerHTML = "";

    data.forEach(ferry => {
        if (ferry.buses.length === 0) return;

        const table = document.createElement("table");
        table.className = "ferry";

        const header = document.createElement("caption");
        header.textContent = `Ferry Departure: ${ferry.ferry_dep}`;
        table.appendChild(header);

        const thead = document.createElement("thead");
        thead.innerHTML = `<tr>
            <th>Bus</th><th>Origin</th><th>Destination</th><th>Dep</th><th>Arr</th><th>First Possible</th>
        </tr>`;
        table.appendChild(thead);

        const tbody = document.createElement("tbody");
        ferry.buses.forEach(bus => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${bus.name}</td>
                <td>${bus.origin}</td>
                <td>${bus.destination}</td>
                <td>${bus.dep}</td>
                <td>${bus.arr}</td>
                <td>${bus.first_possible ? "✅" : ""}</td>
            `;
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        container.appendChild(table);
    });
}

render();
