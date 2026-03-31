/** @odoo-module **/

import { whenReady } from "@odoo/owl";

whenReady(() => {
    document.querySelectorAll("table thead th[data-sort]").forEach((th) => {
        th.style.cursor = "pointer";
        let icon = document.createElement("span");
        icon.style.marginLeft = "5px";
        icon.innerHTML = '<i class="fa fa-chevron-up"></i>';
        th.appendChild(icon);

        th.addEventListener("click", () => {
            const table = th.closest("table");
            const tbody = table.querySelector("tbody.task-blockList");
            if (!tbody) return;

            const index = Array.from(th.parentNode.children).indexOf(th);
            const rows = Array.from(tbody.querySelectorAll(".shortable")).filter(r => r.querySelector("td"));

            const asc = !th.classList.contains("asc");
            table.querySelectorAll("thead th").forEach(h => h.classList.remove("asc", "desc"));
            th.classList.add(asc ? "asc" : "desc");

            rows.sort((a, b) => {
                const A = a.children[index]?.innerText.trim().toLowerCase() || "";
                const B = b.children[index]?.innerText.trim().toLowerCase() || "";

                if (!isNaN(Date.parse(A)) && !isNaN(Date.parse(B))) {
                    return asc ? new Date(A) - new Date(B) : new Date(B) - new Date(A);
                }
                if (!isNaN(A) && !isNaN(B)) {
                    return asc ? A - B : B - A;
                }
                return asc ? A.localeCompare(B) : B.localeCompare(A);
            });

            rows.forEach(r => tbody.appendChild(r));
        });
    });
});
