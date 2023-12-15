DROP DATABASE IF EXISTS `ethbdb`;
CREATE DATABASE IF NOT EXISTS `ethbdb`;
USE `ethbdb`;

CREATE TABLE `locations` (
    `location_x_pos` int(11) NOT NULL,
    `location_y_pos` int(11) NOT NULL,
    CONSTRAINT `PK_locations` PRIMARY KEY (`location_x_pos`, `location_y_pos`),
    `name` varchar(255) NOT NULL UNIQUE
);

CREATE TABLE `planets` (
    `planet_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__planets` PRIMARY KEY (`planet_id`),
    `free_slots` int(11) NOT NULL,
    `location_x_pos` int(11) NOT NULL,
    `location_y_pos` int(11) NOT NULL,
    CONSTRAINT `FK__locations__planets` FOREIGN KEY (`location_x_pos`, `location_y_pos`)
	    REFERENCES `locations` (`location_x_pos`, `location_y_pos`)
);

CREATE TABLE `buildings` (
    `building_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__buildings` PRIMARY KEY (`building_id`),
    `level` int(11) NOT NULL DEFAULT 1,
    `building_type` varchar(255) NOT NULL,
    `planet_id` int(11) NOT NULL,
    CONSTRAINT `FK__planets__buildings` FOREIGN KEY (`planet_id`)
	    REFERENCES `planets` (`planet_id`)
);

CREATE TABLE `guilds` (
    `guild_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__guilds` PRIMARY KEY (`guild_id`),
    `name` varchar(255) NOT NULL UNIQUE,
    `announcement_channel` int(11) NOT NULL,
    `planet_id` int(11) NOT NULL,
    CONSTRAINT `FK__planets__guilds` FOREIGN KEY (`planet_id`)
	    REFERENCES `planets` (`planet_id`)
);

CREATE TABLE `players` (
    `player_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__players` PRIMARY KEY (`player_id`),
    `discord_name` varchar(255) NOT NULL UNIQUE,
    `class` enum('dwarf', 'martian', 'droid') NOT NULL,
    `money` int(11) NOT NULL DEFAULT 0,
    `reputation` int(11) NOT NULL DEFAULT 0,
    `x_pos` int(11) NOT NULL,
    `y_pos` int(11) NOT NULL,
    `guild_id` int(11) NOT NULL,
    CONSTRAINT `FK__guilds__players` FOREIGN KEY (`guild_id`)
	    REFERENCES `guilds` (`guild_id`)
);

CREATE TABLE `reports` (
    `report_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__reports` PRIMARY KEY (`report_id`),
    `content` TEXT NOT NULL,
    `creation_time` TIMESTAMP DEFAULT CURRENT_TIME,
    `player_id` int(11) NOT NULL,
    CONSTRAINT `FK__players__reports` FOREIGN KEY (`player_id`)
	    REFERENCES `players` (`player_id`)
);

CREATE TABLE `polls` (
    `poll_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__polls` PRIMARY KEY (`poll_id`),
    `type` enum('building', 'election') NOT NULL,
    `creation_time` TIMESTAMP DEFAULT CURRENT_TIME
);

CREATE TABLE `votes` (
    `poll_id` int(11) NOT NULL,
    CONSTRAINT `FK__polls__votes` FOREIGN KEY (`poll_id`)
	    REFERENCES `polls` (`poll_id`),
    `player_id` int(11) NOT NULL,
    CONSTRAINT `FK__players__votes` FOREIGN KEY (`player_id`)
	    REFERENCES `players` (`player_id`)
);

CREATE TABLE `ships` (
    `ship_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__ships` PRIMARY KEY (`ship_id`),
    `fuel` int(11) NOT NULL DEFAULT 0,
    `player_id` int(11) NOT NULL,
    CONSTRAINT `FK__players__ships` FOREIGN KEY (`player_id`)
	    REFERENCES `players` (`player_id`)
);

CREATE TABLE `modules` (
    `module_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__modules` PRIMARY KEY (`module_id`),
    `level` int(11) NOT NULL DEFAULT 0,
    `state` enum('active', 'inactive') NULL,
    `type` int(11) NOT NULL,
    `ship_id` int(11) NOT NULL,
    CONSTRAINT `FK__ships__modules` FOREIGN KEY (`ship_id`)
	    REFERENCES `ships` (`ship_id`)
);

CREATE TABLE `cargos` (
    `cargo_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK_cargo_id` PRIMARY KEY (`cargo_id`),
    `module_id` int(11) NOT NULL,
    CONSTRAINT `FK__modules__cargos` FOREIGN KEY (`module_id`)
	    REFERENCES `modules` (`module_id`)
);

-- TODO: Needs a special constraint because an item should be either linked to a building_upgrades or cargos but not on its own.
CREATE TABLE `items` (
    `item_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__items` PRIMARY KEY (`item_id`),
    `amount` int(11) NOT NULL DEFAULT 0,
    `cargo_id` int(11) NULL,
    CONSTRAINT `FK__cargos__items` FOREIGN KEY (`cargo_id`)
	    REFERENCES `cargos` (`cargo_id`)
);

CREATE TABLE `resources` (
    `resource_id` int(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__resources` PRIMARY KEY (`resource_id`),
    `type` enum('copper', 'silver', 'gold', 'uranium', 'black_matter') NOT NULL,
    `item_id` int(11) NOT NULL,
    CONSTRAINT `FK__items__resources` FOREIGN KEY (`item_id`)
	    REFERENCES `items` (`item_id`)
);

CREATE TABLE `building_upgrades` (
    `building_id` int(11) NOT NULL,
    CONSTRAINT `FK__buildings__building_upgrades` FOREIGN KEY (`building_id`)
	    REFERENCES `buildings` (`building_id`),
    `item_id` int(11) NOT NULL,
    CONSTRAINT `FK__items__building_upgrades` FOREIGN KEY (`item_id`)
	    REFERENCES `items` (`item_id`)
);

-- default planets
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
(1, 'The Federation', -1, 2),
(2, 'The Alliance', -1, 3),
(3, 'The Empire', -1, 4),
(4, 'The Independents', -1, 5);
