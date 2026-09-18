OUTPUT_DIRNAME = ".athena"

MANIFEST_FILENAME = "manifest.json"

TREE_DIRNAME = "tree"

ROOT_SUMMARY_FILENAME = "summary.md"

ATHENAIGNORE_FILENAME = ".athenaignore"

# Nomes sempre ignorados, além do .gitignore/.athenaignore do projeto.
ALWAYS_IGNORED_NAMES = {
    ".git",
    OUTPUT_DIRNAME,
}

# Trunca arquivos muito grandes antes de mandar pro Claude, pra não
# estourar custo/tempo em um único arquivo gigante.
MAX_FILE_CHARS = 40_000

# Trava de segurança: recusa indexar mais que isso sem --max-files
# explícito, pra evitar rodar sem querer contra um repositório enorme
# (cada arquivo custa uma chamada real ao Claude).
DEFAULT_MAX_FILES = 300
