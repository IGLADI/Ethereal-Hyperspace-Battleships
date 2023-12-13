CREATE DATABASE IF NOT EXISTS `etherealhyperspacebattleshipsdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `etherealhyperspacebattleshipsdb`;

CREATE TABLE IF NOT EXISTS `building` (
  `building_id` int(11) NOT NULL AUTO_INCREMENT,
  `building_name` varchar(255) NOT NULL,
  `building_cost` int(11) NOT NULL,
  `upgrade_cost` int(11) NOT NULL,
  PRIMARY KEY (`building_id`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `guild` (
  `guild_id` int(11) NOT NULL AUTO_INCREMENT,
  `guild_name` varchar(255) NOT NULL,
  `guild_description` varchar(255) NOT NULL,
  `owned_buildings` text NOT NULL,
  `owned_planets` text NOT NULL,
  `members` text NOT NULL,
  PRIMARY KEY (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `location` (
  `location_id` int(11) NOT NULL AUTO_INCREMENT,
  `x_pos` int(11) NOT NULL,
  `y_pos` int(11) NOT NULL,
  `location_description` varchar(255) NOT NULL,
  PRIMARY KEY (`location_id`),
  UNIQUE KEY `x_pos` (`x_pos`) USING BTREE,
  UNIQUE KEY `y_pos` (`y_pos`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `cargo` (
  `cargo_id` int(11) NOT NULL AUTO_INCREMENT,
  `module_id` int(11) NOT NULL,
  `space` int(11) NOT NULL,
  PRIMARY KEY (`cargo_id`),
  KEY `module_id` (`module_id`)
  CONSTRAINT `FK_module_cargo` FOREIGN KEY (`module_id`) REFERENCES `module` (`module_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `planet` (
  `planet_id` int(11) NOT NULL AUTO_INCREMENT,
  `planet_type` varchar(255) NOT NULL,
  `location_id` int(11) NOT NULL,
  `guild_id` int(11) NOT NULL,
  `resource_id` int(11) NOT NULL,
  PRIMARY KEY (`planet_id`),
  KEY `FK_location` (`location_id`) USING BTREE,
  KEY `FK_guild` (`guild_id`) USING BTREE,
  KEY `FK_resource` (`resource_id`) USING BTREE,
  CONSTRAINT `FK_guild_planet` FOREIGN KEY (`guild_id`) REFERENCES `guild` (`guild_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_location_planet` FOREIGN KEY (`location_id`) REFERENCES `location` (`location_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_resource_planet` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`resource_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `player` (
  `player_id` int(11) NOT NULL AUTO_INCREMENT,
  `player_name` varchar(255) NOT NULL,
  `discord_id` int(19) NOT NULL,
  `money` int(255) NOT NULL DEFAULT 0,
  `x_pos` int(11) NOT NULL,
  `y_pos` int(11) NOT NULL,
  `damage` int(11) NOT NULL,
  `ship` int(11) NOT NULL,
  `fuel` int(11) NOT NULL,
  `player_speed` int(11) NOT NULL,
  `class` enum('Dwarf','Droid','Martian') NOT NULL,
  PRIMARY KEY (`player_id`),
  KEY `FK_xpos_player` (`x_pos`),
  KEY `FK_ypos_player` (`y_pos`),
  CONSTRAINT `FK_x_pos_player` FOREIGN KEY (`x_pos`) REFERENCES `location` (`x_pos`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_y_pos_player` FOREIGN KEY (`y_pos`) REFERENCES `location` (`y_pos`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `resource` (
  `resource_id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(255) NOT NULL,
  `resource_name` varchar(255) NOT NULL,
  `drop_rate` int(11) NOT NULL,
  PRIMARY KEY (`resource_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
