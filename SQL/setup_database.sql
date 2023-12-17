-- more info at https://github.com/LordTlasT/EtHB-docs/blob/main/database

-- Create database
DROP DATABASE IF EXISTS `ethbdb`;
CREATE DATABASE `ethbdb`;
USE `ethbdb`;

-- Create tables --------------------------------------------------------------
CREATE TABLE `locations` (
    `location_x_pos` INT(11) NOT NULL,
    `location_y_pos` INT(11) NOT NULL,
    CONSTRAINT `PK_locations` PRIMARY KEY (`location_x_pos`, `location_y_pos`),
    `name` VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE `planets` (
    `planet_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__planets` PRIMARY KEY (`planet_id`),
    `free_slots` INT(11) NOT NULL,
    `location_x_pos` INT(11) NOT NULL,
    `location_y_pos` INT(11) NOT NULL,
    CONSTRAINT `FK__locations__planets` FOREIGN KEY (`location_x_pos`, `location_y_pos`)
	    REFERENCES `locations` (`location_x_pos`, `location_y_pos`)
);

CREATE TABLE `buildings` (
    `building_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__buildings` PRIMARY KEY (`building_id`),
    `level` INT(11) NOT NULL DEFAULT 1,
    `building_type` VARCHAR(255) NOT NULL,
    `planet_id` INT(11) NOT NULL,
    CONSTRAINT `FK__planets__buildings` FOREIGN KEY (`planet_id`)
	    REFERENCES `planets` (`planet_id`)
);

CREATE TABLE `guilds` (
    `guild_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__guilds` PRIMARY KEY (`guild_id`),
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `planet_id` INT(11) NOT NULL,
    CONSTRAINT `FK__planets__guilds` FOREIGN KEY (`planet_id`)
	    REFERENCES `planets` (`planet_id`)
);

CREATE TABLE `players` (
    `player_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__players` PRIMARY KEY (`player_id`),
    `discord_id` decimal(32) NOT NULL UNIQUE,
    `discord_name` VARCHAR(255) NOT NULL UNIQUE,
    `class` ENUM('dwarf', 'martian', 'droid') NOT NULL,
    `money` INT(11) NOT NULL DEFAULT 1000,
    `reputation` INT(11) NOT NULL DEFAULT 0,
    `x_pos` INT(11) NOT NULL,
    `y_pos` INT(11) NOT NULL,
    `guild_id` INT(11) NOT NULL,
    CONSTRAINT `FK__guilds__players` FOREIGN KEY (`guild_id`)
	    REFERENCES `guilds` (`guild_id`)
);

CREATE TABLE `reports` (
    `report_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__reports` PRIMARY KEY (`report_id`),
    `content` TEXT NOT NULL,
    `creation_time` TIMESTAMP DEFAULT CURRENT_TIME,
    `player_id` INT(11) NOT NULL,
    CONSTRAINT `FK__players__reports` FOREIGN KEY (`player_id`)
	    REFERENCES `players` (`player_id`)
);

CREATE TABLE `polls` (
    `poll_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__polls` PRIMARY KEY (`poll_id`),
    `type` ENUM('building', 'election') NOT NULL,
    `creation_time` TIMESTAMP DEFAULT CURRENT_TIME
);

CREATE TABLE `votes` (
    `poll_id` INT(11) NOT NULL,
    CONSTRAINT `FK__polls__votes` FOREIGN KEY (`poll_id`)
	    REFERENCES `polls` (`poll_id`),
    `player_id` INT(11) NOT NULL,
    CONSTRAINT `FK__players__votes` FOREIGN KEY (`player_id`)
	    REFERENCES `players` (`player_id`),
    `polarity` BOOLEAN NOT NULL
);

CREATE TABLE `modules` (
    `module_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__modules` PRIMARY KEY (`module_id`),
    `level` INT(11) NOT NULL DEFAULT 0,
    `state` ENUM('active', 'inactive') NULL,
    `type` INT(11) NOT NULL
);

CREATE TABLE `ships` (
    `ship_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__ships` PRIMARY KEY (`ship_id`),
    `fuel` INT(11) NOT NULL DEFAULT 0,
    `player_id` INT(11) NOT NULL,
    CONSTRAINT `FK__players__ships` FOREIGN KEY (`player_id`)
	    REFERENCES `players` (`player_id`),
    `module_id` INT(11) NOT NULL,
    CONSTRAINT `FK__modules__ships` FOREIGN KEY (`module_id`)
	    REFERENCES `modules` (`module_id`)
);

CREATE TABLE `cargos` (
    `cargo_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK_cargo_id` PRIMARY KEY (`cargo_id`),
    `module_id` INT(11) NOT NULL,
    CONSTRAINT `FK__modules__cargos` FOREIGN KEY (`module_id`)
	    REFERENCES `modules` (`module_id`)
);

-- TODO: Needs a special constraint because an item should be either linked to a building_upgrades or cargos but not on its own.
CREATE TABLE `items` (
    `item_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__items` PRIMARY KEY (`item_id`),
    `amount` INT(11) NOT NULL DEFAULT 0,
    `cargo_id` INT(11) NULL,
    CONSTRAINT `FK__cargos__items` FOREIGN KEY (`cargo_id`)
	    REFERENCES `cargos` (`cargo_id`)
);

CREATE TABLE `resources` (
    `resource_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__resources` PRIMARY KEY (`resource_id`),
    `type` ENUM('copper', 'silver', 'gold', 'uranium', 'black_matter') NOT NULL,
    `item_id` INT(11) NOT NULL,
    CONSTRAINT `FK__items__resources` FOREIGN KEY (`item_id`)
	    REFERENCES `items` (`item_id`)
);

CREATE TABLE `building_upgrades` (
    `building_id` INT(11) NOT NULL,
    CONSTRAINT `FK__buildings__building_upgrades` FOREIGN KEY (`building_id`)
	    REFERENCES `buildings` (`building_id`),
    `item_id` INT(11) NOT NULL,
    CONSTRAINT `FK__items__building_upgrades` FOREIGN KEY (`item_id`)
	    REFERENCES `items` (`item_id`)
);

-- Setup default values -------------------------------------------------------
-- planets
INSERT INTO `locations` (`location_x_pos`, `location_y_pos`, `name`) VALUES
(0, 0, "Earth"),
(0, 5, "Mars"),
(-5, 5, "Venus"),
(-5, 0, "Jupiter"),
(-5, -5, "Mercury");
-- inserting planet ids manually
INSERT INTO `planets` VALUES
(1, 0, 0, 0),
(2, 3, 0, 5),
(3, 3, -5, 5),
(4, 3, -5, 0),
(5, 3, -5, -5);

-- default guilds
INSERT INTO `guilds`  VALUES
(1, 'The Federation', 2),
(2, 'The Alliance', 3),
(3, 'The Empire', 4),
(4, 'The Independents', 5);
