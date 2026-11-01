export const repository = "https://github.com/lynvera-ai/aidataready";
// Pin documentation and fixtures to the reviewed, public documentation commit.
export const sourceRef = "a7c2c4b3e429617ccb4ad293209e09f2b8e519b6";
export const copy = {
  en: {
    title: "Lynvera AIDataReady | Data readiness for AI",
    description:
      "Open-source Python toolkit for assessing data against contracts for AI, RAG, machine learning and agent tools. Run locally. Review clear reports.",
    skip: "Skip to content",
    guide: "Guide",
    language: "Español",
    eyebrow: "LYNVERA OPEN SOURCE",
    product: "Lynvera AIDataReady",
    headline: ["Know your data.", "Build reliable AI."],
    intro:
      "Check the data before you build on it. Evaluate explicit contracts for AI applications with a local Python library and CLI.",
    start: "Get started",
    github: "View on GitHub",
    version: "Source version",
    python: "Python 3.12+",
    local: ["Local execution", "No model required", "No telemetry"],
    preview: "A contract you can inspect",
    fixture: "Synthetic RAG example",
    previewFoot: "Checks the supplied contract. Does not evaluate a model.",
    profilesLabel: "FOUR PROFILES",
    profilesTitle: "Choose the contract your data needs.",
    profilesIntro:
      "Start with shared checks. Add rules for how your application uses the data.",
    profiles: [
      [
        "General",
        "Required fields, logical types, nulls, unique IDs, ranges, formats, supplied references and freshness.",
      ],
      [
        "RAG",
        "Document IDs, usable text, provenance, versions, exact duplicates and required filter or permission metadata.",
      ],
      [
        "Machine learning",
        "Configured targets, class balance, cardinality, temporal splits and explicitly declared leakage risks.",
      ],
      [
        "Agent tools",
        "Tool fields, documented schemas, contract versions, allowed actions and authorization metadata.",
      ],
    ],
    profilesLink: "Read the profile reference",
    sourcesLabel: "SOURCES",
    sourcesTitle: "Work with the data you already have.",
    sources: [
      ["CSV", "Tabular files"],
      ["JSON", "Arrays of records"],
      ["JSONL", "One record per line"],
      ["Parquet", "Columnar files"],
      ["PostgreSQL", "Read-only access"],
      ["In memory", "Python records"],
    ],
    postgres:
      "PostgreSQL uses allowed tables, bound equality filters, read-only transactions and timeouts. Credentials stay in an environment variable.",
    postgresLink: "PostgreSQL setup",
    workflowLabel: "A REPEATABLE WORKFLOW",
    workflowTitle: "Define. Evaluate. Review.",
    steps: [
      [
        "Define a contract",
        "Choose a source, a profile and the fields and thresholds your application requires.",
      ],
      [
        "Run the assessment",
        "Use the CLI or Python API to check your data locally against that YAML contract.",
      ],
      [
        "Review the findings",
        "Inspect status, severity and violation counts. Keep reports with your development or CI evidence.",
      ],
    ],
    installLabel: "GET STARTED",
    installTitle: "Your first assessment, locally.",
    installIntro:
      "Version {version} is available from source. Use Git and Python 3.12 or newer. These commands pin the reviewed examples and documentation.",
    installCaption: "01 / Install from source",
    os: "macOS / Linux",
    installNote:
      "For Windows, uv and optional dependencies, follow the installation guide.",
    installLink: "Installation guide",
    runCaption: "02 / Run the synthetic RAG example",
    pythonCaption: "Or use the Python API",
    copy: "Copy",
    examplesLabel: "READ THE RESULT",
    examplesTitle: "A passing contract. A known failure.",
    examplesIntro:
      "These are synthetic repository fixtures, not customer data or a live assessment. Both contain two records.",
    passTitle: "RAG documents",
    passText: "The supplied text and metadata satisfy the configured checks.",
    failTitle: "Duplicate IDs",
    failText:
      "Two records share one ID. The uniqueness check reports one violation.",
    expected: "Verified CLI summary",
    exit: "Exit code",
    failNote:
      "FAIL exits 1. Run report conversion separately after that expected failure.",
    date: "Examples verified November 1, 2026. The RAG fixture uses fixed dates and a 3,650-day freshness window.",
    outcomes:
      "PASS and WARN exit 0. FAIL exits 1. ERROR and INCONCLUSIVE exit 2. Empty or partial evidence cannot establish a passing scan.",
    reportsLabel: "REPORTS",
    reportsTitle: "Keep evidence in the format you use.",
    reports: [
      [
        "JSON",
        "Structured findings and aggregate statistics. Preserves each original status.",
      ],
      [
        "HTML",
        "A local report with severity, category and source filters. No external assets.",
      ],
      [
        "JUnit",
        "XML for CI. WARN and INCONCLUSIVE map to skipped tests, so retain JSON when those distinctions matter.",
      ],
    ],
    download: "Download synthetic example",
    reportCaption: "Convert a saved result",
    reportNote:
      "Report conversion does not rescan data. Reports contain counts and field names, without record samples.",
    docsLabel: "DOCUMENTATION",
    docsTitle: "Go from a first check to your own contract.",
    docs: [
      "Installation",
      "CLI reference",
      "Python API",
      "Profiles",
      "PostgreSQL",
      "Contract reference",
    ],
    faqTitle: "Questions, answered.",
    faq: [
      [
        "Does PASS certify that my AI will perform well?",
        "No. Assessments check the supplied data contract. They do not certify model performance, retrieval relevance, semantic quality or effective access permissions.",
      ],
      [
        "Does my data leave my machine?",
        "Local file and in-memory assessments do not upload your data. The package sends no telemetry. PostgreSQL connects to the database you configure. Installing dependencies usually needs network access.",
      ],
      [
        "Is sensitive data detection definitive?",
        "No. Optional sensitive data detection is heuristic. It can miss sensitive data or flag ordinary values. Review the findings and your own privacy requirements.",
      ],
      [
        "Are batch budgets absolute memory limits?",
        "No. Batch budgets are checked after decoding and are not hard process memory caps. Distinct tracking is also bounded. Incomplete evidence may produce INCONCLUSIVE.",
      ],
      [
        "Do I need a model, account or paid service?",
        "No. The synthetic examples run locally after installation. PostgreSQL requires your own database and its optional driver.",
      ],
      [
        "Can I install the package from PyPI?",
        "The reviewed 0.1.0 project is distributed from source. Use the source installation shown here and check the repository release guidance before upgrading.",
      ],
    ],
    closing: "Make the contract explicit.",
    closingText:
      "Start with the included data. Then define what your own application needs.",
    author: "Created and maintained by Dr. Felipe Castillo Rendón.",
    contact: "Contact",
    license: "Apache License 2.0",
    notFound: "Page not found",
    home: "Go to the English site",
  },
  es: {
    title: "Lynvera AIDataReady | Evaluación de datos para IA",
    description:
      "Herramienta Python de código abierto para evaluar contratos de datos para IA, RAG, machine learning y herramientas de agentes. Ejecución e informes locales.",
    skip: "Saltar al contenido",
    guide: "Guía",
    language: "English",
    eyebrow: "LYNVERA OPEN SOURCE",
    product: "Lynvera AIDataReady",
    headline: ["Conoce tus datos.", "Construye IA confiable."],
    intro:
      "Revisa los datos antes de construir con ellos. Evalúa contratos explícitos para aplicaciones de IA con una biblioteca Python y una CLI locales.",
    start: "Comenzar",
    github: "Ver en GitHub",
    version: "Versión desde código fuente",
    python: "Python 3.12+",
    local: ["Ejecución local", "Sin modelos", "Sin telemetría"],
    preview: "Un contrato que puedes revisar",
    fixture: "Ejemplo RAG sintético",
    previewFoot: "Verifica el contrato suministrado. No evalúa un modelo.",
    profilesLabel: "CUATRO PERFILES",
    profilesTitle: "Elige el contrato que necesitan tus datos.",
    profilesIntro:
      "Parte de comprobaciones generales. Agrega reglas según el uso de los datos en tu aplicación.",
    profiles: [
      [
        "General",
        "Campos obligatorios, tipos lógicos, nulos, IDs únicos, rangos, formatos, referencias suministradas y vigencia.",
      ],
      [
        "RAG",
        "IDs de documentos, texto utilizable, procedencia, versiones, duplicados exactos y metadatos de filtros o permisos requeridos.",
      ],
      [
        "Machine learning",
        "Objetivo configurado, balance de clases, cardinalidad, divisiones temporales y riesgos de fuga declarados explícitamente.",
      ],
      [
        "Herramientas de agentes",
        "Campos de herramientas, esquemas documentados, versiones de contrato, acciones permitidas y metadatos de autorización.",
      ],
    ],
    profilesLink: "Consultar los perfiles",
    sourcesLabel: "FUENTES",
    sourcesTitle: "Trabaja con los datos que ya tienes.",
    sources: [
      ["CSV", "Archivos tabulares"],
      ["JSON", "Arreglos de registros"],
      ["JSONL", "Un registro por línea"],
      ["Parquet", "Archivos columnares"],
      ["PostgreSQL", "Acceso de solo lectura"],
      ["En memoria", "Registros de Python"],
    ],
    postgres:
      "PostgreSQL usa tablas permitidas, filtros de igualdad parametrizados, transacciones de solo lectura y tiempos de espera. Las credenciales permanecen en una variable de entorno.",
    postgresLink: "Configurar PostgreSQL",
    workflowLabel: "UN FLUJO REPETIBLE",
    workflowTitle: "Define. Evalúa. Revisa.",
    steps: [
      [
        "Define un contrato",
        "Elige una fuente, un perfil y los campos y umbrales que necesita tu aplicación.",
      ],
      [
        "Ejecuta la evaluación",
        "Usa la CLI o la API Python para contrastar tus datos localmente con el contrato YAML.",
      ],
      [
        "Revisa los hallazgos",
        "Consulta estado, severidad y conteos de incumplimientos. Conserva los informes como evidencia de desarrollo o CI.",
      ],
    ],
    installLabel: "COMENZAR",
    installTitle: "Tu primera evaluación, en local.",
    installIntro:
      "La versión {version} está disponible desde el código fuente. Usa Git y Python 3.12 o posterior. Estos comandos fijan los ejemplos y la documentación revisados.",
    installCaption: "01 / Instalar desde código fuente",
    os: "macOS / Linux",
    installNote:
      "Para Windows, uv y dependencias opcionales, consulta la guía de instalación.",
    installLink: "Guía de instalación",
    runCaption: "02 / Ejecutar el ejemplo RAG sintético",
    pythonCaption: "O usa la API Python",
    copy: "Copiar",
    examplesLabel: "INTERPRETA EL RESULTADO",
    examplesTitle: "Un contrato que cumple. Un fallo conocido.",
    examplesIntro:
      "Son datos sintéticos del repositorio, no datos de clientes ni una evaluación en vivo. Ambos ejemplos contienen dos registros.",
    passTitle: "Documentos RAG",
    passText:
      "El texto y los metadatos suministrados cumplen las comprobaciones configuradas.",
    failTitle: "IDs duplicados",
    failText:
      "Dos registros comparten un ID. La comprobación de unicidad reporta un incumplimiento.",
    expected: "Resumen de CLI verificado",
    exit: "Código de salida",
    failNote:
      "FAIL termina con código 1. Ejecuta la conversión del informe por separado después de ese fallo esperado.",
    date: "Ejemplos verificados el 1 de noviembre de 2026. Los datos RAG usan fechas fijas y una ventana de vigencia de 3,650 días.",
    outcomes:
      "PASS y WARN terminan con 0. FAIL termina con 1. ERROR e INCONCLUSIVE terminan con 2. La evidencia vacía o parcial no permite concluir que el análisis cumple.",
    reportsLabel: "INFORMES",
    reportsTitle: "Conserva la evidencia en tu formato habitual.",
    reports: [
      [
        "JSON",
        "Hallazgos estructurados y estadísticas agregadas. Conserva cada estado original.",
      ],
      [
        "HTML",
        "Informe local con filtros por severidad, categoría y fuente. Sin recursos externos.",
      ],
      [
        "JUnit",
        "XML para CI. WARN e INCONCLUSIVE se representan como pruebas omitidas; conserva el JSON si necesitas distinguirlos.",
      ],
    ],
    download: "Descargar ejemplo sintético",
    reportCaption: "Convertir un resultado guardado",
    reportNote:
      "La conversión no vuelve a analizar los datos. Los informes contienen conteos y nombres de campos, sin muestras de registros.",
    docsLabel: "DOCUMENTACIÓN",
    docsTitle: "Pasa del primer análisis a tu propio contrato.",
    docs: [
      "Instalación",
      "Referencia de CLI",
      "API Python",
      "Perfiles",
      "PostgreSQL",
      "Referencia de contratos",
    ],
    faqTitle: "Preguntas frecuentes.",
    faq: [
      [
        "¿PASS certifica que mi IA funcionará bien?",
        "No. Las evaluaciones verifican el contrato de datos suministrado. No certifican rendimiento de modelos, relevancia de recuperación, calidad semántica ni permisos efectivos de acceso.",
      ],
      [
        "¿Mis datos salen de mi equipo?",
        "Las evaluaciones de archivos locales y memoria no suben tus datos. El paquete no envía telemetría. PostgreSQL se conecta a la base que configures. Instalar dependencias normalmente requiere conexión.",
      ],
      [
        "¿La detección de datos sensibles es definitiva?",
        "No. La detección opcional es heurística. Puede omitir datos sensibles o marcar valores comunes. Revisa los hallazgos y tus propios requisitos de privacidad.",
      ],
      [
        "¿Los presupuestos por lote son límites absolutos de memoria?",
        "No. Se comprueban después de decodificar y no limitan de forma absoluta la memoria del proceso. El seguimiento de valores distintos también tiene límites. La evidencia incompleta puede producir INCONCLUSIVE.",
      ],
      [
        "¿Necesito un modelo, cuenta o servicio de pago?",
        "No. Los ejemplos sintéticos se ejecutan localmente después de instalar. PostgreSQL requiere tu propia base y el controlador opcional.",
      ],
      [
        "¿Puedo instalar el paquete desde PyPI?",
        "El proyecto revisado en su versión 0.1.0 se distribuye desde código fuente. Usa la instalación indicada y consulta la guía de versiones del repositorio antes de actualizar.",
      ],
    ],
    closing: "Haz explícito el contrato.",
    closingText:
      "Comienza con los datos incluidos. Después define lo que necesita tu aplicación.",
    author: "Creado y mantenido por Dr. Felipe Castillo Rendón.",
    contact: "Contacto",
    license: "Apache License 2.0",
    notFound: "Página no encontrada",
    home: "Ir al sitio en español",
  },
};
