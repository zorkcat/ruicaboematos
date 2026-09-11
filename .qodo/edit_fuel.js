const fs = require("fs");
const path = "c:\\Users\\User\\Desktop\\website real\\index.html";
let html = fs.readFileSync(path, "utf8");

function apply(label, from, to) {
  const idx = html.indexOf(from);
  if (idx === -1) throw new Error("NOT FOUND: " + label);
  html = html.slice(0, idx) + to + html.slice(idx + from.length);
  console.log("OK  " + label);
}

// ---- Combustible por trator (feito + chip na grella) ----
apply(
  "yanmar fuel",
  '            brandFilter: "yanmar",\n            image: "yanmar.png",',
  '            brandFilter: "yanmar",\n            fuel: "Gasóleo",\n            image: "yanmar.png",'
);
apply(
  "yanmar features",
  '                "1.983 h",\n                "2023"\n            ]',
  '                "1.983 h",\n                "2023",\n                "Gasóleo"\n            ]'
);

apply(
  "same7699 fuel",
  '            model: "FRUTTETO 75",',
  '            model: "FRUTTETO 75",\n            fuel: "Gasóleo",'
);
apply(
  "same7699 features",
  '                "5.784 h",\n                "1999"\n            ]',
  '                "5.784 h",\n                "1999",\n                "Gasóleo"\n            ]'
);

apply(
  "same7600 fuel",
  '            model: "FRUTTETO 75 CAB.",',
  '            model: "FRUTTETO 75 CAB.",\n            fuel: "Gasóleo",'
);
apply(
  "same7600 features",
  '                "5.305 h",\n                "2000"\n            ]',
  '                "5.305 h",\n                "2000",\n                "Gasóleo"\n            ]'
);

apply(
  "tym fuel",
  '            model: "T303 — Carregador Frontal",',
  '            model: "T303 — Carregador Frontal",\n            fuel: "Gasóleo",'
);
apply(
  "tym features",
  '                "109,2 h",\n                "Carregador frontal"\n            ]',
  '                "109,2 h",\n                "Carregador frontal",\n                "Gasóleo"\n            ]'
);

apply(
  "solis fuel",
  '            model: "S26+",',
  '            model: "S26+",\n            fuel: "Gasóleo",'
);
apply(
  "solis features",
  '                "0 h",\n                "Direção assistida"\n            ]',
  '                "0 h",\n                "Direção assistida",\n                "Gasóleo"\n            ]'
);

apply(
  "kubota fuel",
  '            model: "L2550",',
  '            model: "L2550",\n            fuel: "Gasóleo",'
);
apply(
  "kubota features",
  '                "4.274 h",\n                "Matriculado"\n            ]',
  '                "4.274 h",\n                "Matriculado",\n                "Gasóleo"\n            ]'
);

apply(
  "husqvarna fuel",
  '            model: "CTH191 19CV",',
  '            model: "CTH191 19CV",\n            fuel: "Gasolina",'
);
apply(
  "husqvarna features",
  '                "Motor Kohler",\n                "2009"\n            ]',
  '                "Motor Kohler",\n                "2009",\n                "Gasolina"\n            ]'
);

apply(
  "ford fuel",
  '            model: "3910",',
  '            model: "3910",\n            fuel: "Gasóleo",'
);
apply(
  "ford features",
  '                "3.191 h",\n                "Matriculado"\n            ]',
  '                "3.191 h",\n                "Matriculado",\n                "Gasóleo"\n            ]'
);

apply(
  "kioti fuel",
  '            model: "DK5010N",',
  '            model: "DK5010N",\n            fuel: "Gasóleo",'
);
apply(
  "kioti features",
  '                "3.300 h",\n                "2019"\n            ]',
  '                "3.300 h",\n                "2019",\n                "Gasóleo"\n            ]'
);

// ---- Cards: 5 chips ----
apply(
  "slice 5",
  "                        .slice(0,4)",
  "                        .slice(0,5)"
);

// ---- Busqueda: inclúe combustible ----
apply(
  "search fuel",
  "                                tractor.hours\n                            ].join(\" \")",
  "                                tractor.hours,\n                                tractor.fuel\n                            ].join(\" \")"
);

// ---- Modal: spec Combustível ----
apply(
  "modal fuel spec",
  `            <div class="modal-spec">

                <i class="fas fa-calendar"></i>

                <div>

                    <small>
                        Ano
                    </small>

                    <strong>
                        \${escapeHtml(
                            tractor.year
                        )}
                    </strong>

                </div>

            </div>

        \`;`,
  `            <div class="modal-spec">

                <i class="fas fa-calendar"></i>

                <div>

                    <small>
                        Ano
                    </small>

                    <strong>
                        \${escapeHtml(
                            tractor.year
                        )}
                    </strong>

                </div>

            </div>


            <div class="modal-spec">

                <i class="fas fa-gas-pump"></i>

                <div>

                    <small>
                        Combustível
                    </small>

                    <strong>
                        \${escapeHtml(
                            tractor.fuel
                        )}
                    </strong>

                </div>

            </div>

        \`;`
);

fs.writeFileSync(path, html, "utf8");
console.log("DONE");