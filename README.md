# Manage Local Neo4j Databases

The `neo4j-db-manager` tool provides simple actions for managing multiple Neo4j databases. It allows three verbs:

1. **List** all available Neo4j databases (`.db` directories).
2. **Switch** the Neo4j configuration file to point to a new database.
3. **Remove** a Neo4j database directory.

The locations of the Neo4j configuration file and database directory can either be specified in the CLI command or stored in a JSON text file located at `~/.ndeo4jdbprofile`.

## Requirements

- Python 2.7
- [docopt](https://github.com/docopt/docopt)

## Future Plans

- Mark currently-selected database in `ls`.
- Simplify path and conf file checking.
