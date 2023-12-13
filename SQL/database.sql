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

