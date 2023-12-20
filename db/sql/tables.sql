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
    `slots` INT(11) NOT NULL,
    `location_x_pos` INT(11) NOT NULL,
    `location_y_pos` INT(11) NOT NULL,
    CONSTRAINT `FK__locations__planets` FOREIGN KEY (`location_x_pos`, `location_y_pos`)
	    REFERENCES `locations` (`location_x_pos`, `location_y_pos`)
);

CREATE TABLE `buildings` (
    `building_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__buildings` PRIMARY KEY (`building_id`),
    `level` INT(11) NOT NULL DEFAULT 1,
    `type` ENUM('repair station', 'shop', 'outpost', 'factory', 'mining station', 'sace warp', 'trading station', 'casino') NOT NULL,
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
    `discord_id` DECIMAL(32) NOT NULL UNIQUE,
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

CREATE TABLE `ships` (
    `ship_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__ships` PRIMARY KEY (`ship_id`),
    `fuel` INT(11) NOT NULL DEFAULT 0,
    `player_id` INT(11) NOT NULL,
    CONSTRAINT `FK__players__ships` FOREIGN KEY (`player_id`)
	    REFERENCES `players` (`player_id`)
);

CREATE TABLE `modules` (
    `module_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__modules` PRIMARY KEY (`module_id`),
    `level` INT(11) NOT NULL DEFAULT 0,
    `state` ENUM('active', 'inactive') NULL,
    `type` ENUM('SolarPanel', 'TravelModule', 'MiningModule', 'Canon', 'Shield', 'Fuel', 'Cargo', 'Radar', 'EnergyGenerator') NOT NULL,
    `ship_id` INT(11) NOT NULL,
    CONSTRAINT `FK__ships__modules` FOREIGN KEY (`ship_id`)
	    REFERENCES `ships` (`ship_id`),
    CONSTRAINT `UN__modules` UNIQUE (type, ship_id)
);

CREATE TABLE `fuel_modules` (
    `fuel_module_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK_fuel_module_id` PRIMARY KEY (`fuel_module_id`),
    `fuel` int(11) NOT NULL DEFAULT 100,
    `module_id` INT(11) NOT NULL,
    CONSTRAINT `FK__modules__fuel_modules` FOREIGN KEY (`module_id`)
	    REFERENCES `modules` (`module_id`)
);

CREATE TABLE `cargo_modules` (
    `cargo_module_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK_cargo_module_id` PRIMARY KEY (`cargo_module_id`),
    `module_id` INT(11) NOT NULL,
    CONSTRAINT `FK__modules__cargo_modules` FOREIGN KEY (`module_id`)
	    REFERENCES `modules` (`module_id`)
);

CREATE TABLE `items` (
    `item_id` INT(11) NOT NULL AUTO_INCREMENT,
    CONSTRAINT `PK__items` PRIMARY KEY (`item_id`),
    `name` ENUM('rock', 'copper', 'silver', 'gold', 'uranium', 'black matter') NOT NULL,
    `type` ENUM('resource') NOT NULL,
    `amount` INT(11) NOT NULL DEFAULT 1,
    `cargo_module_id` int(11) NULL,
    CONSTRAINT `FK__cargo_modules__items` FOREIGN KEY (`cargo_module_id`)
	    REFERENCES `cargo_modules` (`cargo_module_id`),
    CONSTRAINT `UN__items` UNIQUE (`name`, `cargo_module_id`)
);

-- TODO UPDATE DOCUMENATION
CREATE TABLE `contributions` (
    `building_id` INT(11) NOT NULL,
    CONSTRAINT `FK__buildings__contributions` FOREIGN KEY (`building_id`)
	    REFERENCES `buildings` (`building_id`),
    `item_id` INT(11) NOT NULL,
    CONSTRAINT `FK__items__contributions` FOREIGN KEY (`item_id`)
	    REFERENCES `items` (`item_id`),
    CONSTRAINT `UN__contributions` UNIQUE (building_id, item_id)
);

-- Setup default values -------------------------------------------------------
-- planets
INSERT INTO `locations` (`location_x_pos`, `location_y_pos`, `name`) VALUES
(0, 0, 'Earth'),
(0, 5, 'Mars'),
(-5, 5, 'Venus'),
(-5, 0, 'Jupiter'),
(-5, -5, 'Mercury');
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
