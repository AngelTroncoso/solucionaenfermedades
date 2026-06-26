//#region src/lib/discoveries.ts
var DISCOVERIES = [
	{
		id: "d-001",
		timestamp: "2050.06.24 — 14:32:10",
		status: "PUBLICABLE",
		drug: "Montelukast + Dupilumab",
		disease: "Rinitis Alérgica Crónica",
		fitness: .847,
		area: "Inmunología / Alergología",
		mechanism: "Bloqueo dual IL-4Rα + antagonismo CYSLT1 con reducción eosinofílica",
		paper: true,
		journal: "Nature Medicine"
	},
	{
		id: "d-002",
		timestamp: "2050.06.24 — 13:58:42",
		status: "PUBLICABLE",
		drug: "Omalizumab + Bilastina",
		disease: "Rinitis Alérgica Perenne",
		fitness: .823,
		area: "Inmunología",
		mechanism: "Neutralización IgE libre + bloqueo H1 selectivo sin sedación",
		paper: true,
		journal: "Journal of Allergy and Clinical Immunology"
	},
	{
		id: "d-003",
		timestamp: "2050.06.24 — 12:11:05",
		status: "EN REVISIÓN",
		drug: "Azitromicina baja dosis + Ciclesonida",
		disease: "Rinosinusitis Crónica",
		fitness: .791,
		area: "ORL / Inmunología",
		mechanism: "Inmunomodulación macrolida + supresión glucocorticoide local",
		paper: false
	},
	{
		id: "d-004",
		timestamp: "2050.06.24 — 11:04:21",
		status: "PUBLICABLE",
		drug: "Ketotifeno + Rupatadina",
		disease: "Alergia al Polvo Doméstico",
		fitness: .812,
		area: "Alergología",
		mechanism: "Estabilización mastocitos + bloqueo H1/PAF dual",
		paper: true,
		journal: "Allergy"
	}
];
var MOLECULES = [
	{
		name: "Montelukast",
		target: "CYSLT1",
		patent: "genérico",
		moa: "Antagonista selectivo del receptor de leucotrienos LTD4."
	},
	{
		name: "Dupilumab",
		target: "IL-4Rα",
		patent: "vigente",
		moa: "Anticuerpo monoclonal anti IL-4/IL-13, modulador Th2."
	},
	{
		name: "Omalizumab",
		target: "IgE libre",
		patent: "vigente",
		moa: "Anti-IgE recombinante, bloquea unión a FcεRI."
	},
	{
		name: "Bilastina",
		target: "H1",
		patent: "genérico",
		moa: "Antihistamínico H1 de segunda generación no sedante."
	},
	{
		name: "Ciclesonida",
		target: "GR nuclear",
		patent: "genérico",
		moa: "Pro-fármaco corticoide intranasal activado por esterasas."
	},
	{
		name: "Azitromicina",
		target: "50S ribosomal",
		patent: "genérico",
		moa: "Macrólido con efecto inmunomodulador a baja dosis."
	},
	{
		name: "Ketotifeno",
		target: "Mastocito / H1",
		patent: "genérico",
		moa: "Estabilizador de mastocitos y antihistamínico."
	},
	{
		name: "Rupatadina",
		target: "H1 / PAF",
		patent: "vigente",
		moa: "Dual antagonista H1 y PAF."
	},
	{
		name: "Fluticasona",
		target: "GR nuclear",
		patent: "genérico",
		moa: "Corticoide intranasal de alta potencia."
	},
	{
		name: "Mepolizumab",
		target: "IL-5",
		patent: "vigente",
		moa: "Anti-IL-5 anticuerpo monoclonal, reductor eosinofílico."
	}
];
var JOURNALS = [
	{
		name: "Nature Medicine",
		impact: 58.7
	},
	{
		name: "The Lancet",
		impact: 202.7
	},
	{
		name: "NEJM",
		impact: 176.1
	},
	{
		name: "Allergy",
		impact: 12.4
	},
	{
		name: "Journal of Allergy and Clinical Immunology",
		impact: 14.2
	}
];
var FITNESS_EVOLUTION = [
	{
		gen: 1,
		fitness: .32
	},
	{
		gen: 2,
		fitness: .41
	},
	{
		gen: 3,
		fitness: .48
	},
	{
		gen: 4,
		fitness: .55
	},
	{
		gen: 5,
		fitness: .61
	},
	{
		gen: 6,
		fitness: .66
	},
	{
		gen: 7,
		fitness: .72
	},
	{
		gen: 8,
		fitness: .77
	},
	{
		gen: 9,
		fitness: .81
	},
	{
		gen: 10,
		fitness: .823
	},
	{
		gen: 11,
		fitness: .835
	},
	{
		gen: 12,
		fitness: .847
	}
];
//#endregion
export { MOLECULES as i, FITNESS_EVOLUTION as n, JOURNALS as r, DISCOVERIES as t };
