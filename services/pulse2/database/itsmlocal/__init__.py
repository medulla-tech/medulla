# file : services/pulse2/database/itsmlocal/__init__.py

"""Database access for the Medulla itsmlocal database."""

from mmc.database.database_helper import DatabaseHelper
from sqlalchemy import create_engine, text

from pulse2.database.itsmlocal.schema import Tests


class ItsmlocalDatabase(DatabaseHelper):
    """Provide the database connection used by the itsmlocal plugin."""

    is_activated = False
    session = None

    def db_check(self):
        """Check the module-owned database configuration."""
        self.my_name = "itsmlocal"
        self.configfile = "itsmlocal.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        """Initialize the SQLAlchemy engine when the plugin is enabled."""
        if self.is_activated:
            return True
        self.config = config
        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
            pool_timeout=self.config.dbpooltimeout,
        )
        if not self.db_check():
            return False
        self.is_activated = True
        return True

    def tests(self):
        """Return module health-check rows."""
        return []

    def create_client_root(self, client_name):
        """Create one ITSMLocal client root directly below Medulla.

        Client roots are allocated locally before their remote ITSM access is
        configured. Their local id is subsequently the scope used by the
        configuration and reconciliation mappings.
        """
        name = str(client_name or "").strip()
        if not name:
            raise ValueError("client root name is required")

        with self.db.begin() as connection:
            connection.execute(
                text("SELECT GET_LOCK(:name, 30)"),
                {"name": "itsmlocal_entity_alloc"},
            )
            try:
                existing_id = connection.execute(
                    text(
                        "SELECT `id` FROM `glpi_entities` "
                        "WHERE `entities_id` = 0 AND `name` = :name"
                    ),
                    {"name": name},
                ).scalar()
                if existing_id is not None:
                    return int(existing_id)

                local_id = connection.execute(
                    text("SELECT COALESCE(MAX(`id`), 0) + 1 FROM `glpi_entities`")
                ).scalar()
                local_id = int(local_id or 1)
                connection.execute(
                    text(
                        """
                        INSERT INTO `glpi_entities`
                            (`id`, `name`, `entities_id`, `completename`, `level`,
                             `sons_cache`, `ancestors_cache`, `date_mod`, `date_creation`)
                        VALUES
                            (:id, :name, 0, :completename, 2,
                             '[]', NULL, NOW(), NOW())
                        """
                    ),
                    {
                        "id": local_id,
                        "name": name,
                        "completename": f"Medulla/{name}",
                    },
                )
                return local_id
            finally:
                connection.execute(
                    text("SELECT RELEASE_LOCK(:name)"),
                    {"name": "itsmlocal_entity_alloc"},
                )

    def disable_client_root_users(self, client_name):
        """Disable users assigned to one client root and its descendants.

        ITSMLocal entities have no native active flag. The entity tree is kept
        intact for audit and possible restoration, while its users are made
        unable to authenticate in GLPI.
        """
        name = str(client_name or "").strip()
        if not name:
            raise ValueError("client root name is required")

        with self.db.begin() as connection:
            root = (
                connection.execute(
                    text(
                        "SELECT `id`, `completename` FROM `glpi_entities` "
                        "WHERE `entities_id` = 0 AND `name` = :name"
                    ),
                    {"name": name},
                )
                .mappings()
                .first()
            )
            if root is None:
                raise ValueError("client root does not exist")

            root_path = str(root["completename"] or f"Medulla/{name}")
            result = connection.execute(
                text(
                    """
                    UPDATE `glpi_users` AS `user`
                    INNER JOIN (
                        SELECT DISTINCT `users_id` AS `id`
                        FROM `glpi_profiles_users`
                        WHERE `entities_id` IN (
                            SELECT `id` FROM `glpi_entities`
                            WHERE `completename` = :root_path
                               OR `completename` LIKE CONCAT(:root_path, '/%')
                        )
                        UNION
                        SELECT `id` FROM `glpi_users`
                        WHERE `entities_id` IN (
                            SELECT `id` FROM `glpi_entities`
                            WHERE `completename` = :root_path
                               OR `completename` LIKE CONCAT(:root_path, '/%')
                        )
                    ) AS `scoped_user` ON `scoped_user`.`id` = `user`.`id`
                    SET `user`.`is_active` = 0, `user`.`date_mod` = NOW()
                    WHERE `user`.`is_active` <> 0 AND `user`.`name` <> 'root'
                    """
                ),
                {"root_path": root_path},
            )
            return {"entity_id": int(root["id"]), "disabled_users": result.rowcount}
