-- MySQL dump 10.13  Distrib 5.1.69, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: iggybase_admin
-- ------------------------------------------------------
-- Server version	5.1.69-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `action`
--

DROP TABLE IF EXISTS `action`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `action` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `action_value` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `action`
--

LOCK TABLES `action` WRITE;
/*!40000 ALTER TABLE `action` DISABLE KEYS */;
/*!40000 ALTER TABLE `action` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `data_type`
--

DROP TABLE IF EXISTS `data_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_type`
--

LOCK TABLES `data_type` WRITE;
/*!40000 ALTER TABLE `data_type` DISABLE KEYS */;
INSERT INTO `data_type` VALUES (1,'Integer','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL),(2,'String','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL),(3,'Boolean','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL),(4,'DateTime','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL),(5,'File','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL);
/*!40000 ALTER TABLE `data_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facility`
--

DROP TABLE IF EXISTS `facility`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `facility` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facility`
--

LOCK TABLES `facility` WRITE;
/*!40000 ALTER TABLE `facility` DISABLE KEYS */;
INSERT INTO `facility` VALUES (1,'RC','Research Computing','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL);
/*!40000 ALTER TABLE `facility` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `facility_role`
--

DROP TABLE IF EXISTS `facility_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `facility_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `facility_id` int(11) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `role_id` (`role_id`),
  KEY `facility_id` (`facility_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facility_role`
--

LOCK TABLES `facility_role` WRITE;
/*!40000 ALTER TABLE `facility_role` DISABLE KEYS */;
INSERT INTO `facility_role` VALUES (1,'RC Admin',NULL,NULL,NULL,NULL,NULL,NULL,1,1),(2,'RC CoreUser',NULL,NULL,NULL,NULL,NULL,NULL,1,2);
/*!40000 ALTER TABLE `facility_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `field`
--

DROP TABLE IF EXISTS `field`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `field` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `display_name` varchar(100) DEFAULT NULL,
  `table_object_id` int(11) DEFAULT NULL,
  `data_type_id` int(11) DEFAULT NULL,
  `unique` tinyint(1) DEFAULT NULL,
  `primary_key` tinyint(1) DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  `default` varchar(255) DEFAULT NULL,
  `foreign_key_table_object_id` int(11) DEFAULT NULL,
  `foreign_key_field_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `display_name` (`name`),
  KEY `type_id` (`table_object_id`)
) ENGINE=MyISAM AUTO_INCREMENT=129 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `field`
--

LOCK TABLES `field` WRITE;
/*!40000 ALTER TABLE `field` DISABLE KEYS */;
INSERT INTO `field` VALUES (61,'F000061',NULL,NULL,NULL,1,NULL,NULL,'id',1,1,NULL,1,11,NULL,NULL,NULL),(62,'F000062',NULL,NULL,NULL,1,NULL,NULL,'name',1,2,1,NULL,50,NULL,NULL,NULL),(63,'F000063',NULL,NULL,NULL,1,NULL,NULL,'description',1,2,NULL,NULL,255,NULL,NULL,NULL),(64,'F000064',NULL,NULL,NULL,1,NULL,NULL,'date_created',1,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(65,'F000065',NULL,NULL,NULL,1,NULL,NULL,'last_modified',1,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(66,'F000066',NULL,NULL,NULL,1,NULL,NULL,'active',1,3,NULL,NULL,1,NULL,NULL,NULL),(67,'F000067',NULL,NULL,NULL,1,NULL,NULL,'organization_id',1,1,NULL,NULL,11,NULL,4,28),(68,'F000068',NULL,NULL,NULL,1,NULL,NULL,'order',1,1,NULL,NULL,11,NULL,NULL,NULL),(69,'F000069',NULL,NULL,NULL,1,NULL,NULL,'address_1',1,2,NULL,NULL,100,NULL,NULL,NULL),(70,'F000070',NULL,NULL,NULL,1,NULL,NULL,'address_2',1,2,NULL,NULL,100,NULL,NULL,NULL),(71,'F000071',NULL,NULL,NULL,1,NULL,NULL,'city',1,2,NULL,NULL,100,NULL,NULL,NULL),(72,'F000072',NULL,NULL,NULL,1,NULL,NULL,'state',1,2,NULL,NULL,100,NULL,NULL,NULL),(73,'F000073',NULL,NULL,NULL,1,NULL,NULL,'postcode',1,2,NULL,NULL,100,NULL,NULL,NULL),(74,'F000074',NULL,NULL,NULL,1,NULL,NULL,'country',1,2,NULL,NULL,100,NULL,NULL,NULL),(75,'F000075',NULL,NULL,NULL,1,NULL,NULL,'id',2,1,NULL,1,11,NULL,NULL,NULL),(76,'F000076',NULL,NULL,NULL,1,NULL,NULL,'name',2,2,1,NULL,50,NULL,NULL,NULL),(77,'F000077',NULL,NULL,NULL,1,NULL,NULL,'description',2,2,NULL,NULL,255,NULL,NULL,NULL),(78,'F000078',NULL,NULL,NULL,1,NULL,NULL,'date_created',2,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(79,'F000079',NULL,NULL,NULL,1,NULL,NULL,'last_modified',2,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(87,'F000087',NULL,NULL,NULL,1,NULL,NULL,'active',2,3,NULL,NULL,1,NULL,NULL,NULL),(88,'F000088',NULL,NULL,NULL,1,NULL,NULL,'organization_id',2,1,NULL,NULL,11,NULL,4,28),(89,'F000089',NULL,NULL,NULL,1,NULL,NULL,'order',2,1,NULL,NULL,11,NULL,NULL,NULL),(90,'F000090',NULL,NULL,NULL,1,NULL,NULL,'address_id',2,1,NULL,NULL,11,NULL,1,61),(91,'F000091',NULL,NULL,NULL,1,NULL,NULL,'id',3,1,NULL,1,11,NULL,NULL,NULL),(92,'F000092',NULL,NULL,NULL,1,NULL,NULL,'name',3,2,1,NULL,50,NULL,NULL,NULL),(93,'F000093',NULL,NULL,NULL,1,NULL,NULL,'description',3,2,NULL,NULL,255,NULL,NULL,NULL),(94,'F000094',NULL,NULL,NULL,1,NULL,NULL,'date_created',3,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(95,'F000095',NULL,NULL,NULL,1,NULL,NULL,'last_modified',3,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(96,'F000096',NULL,NULL,NULL,1,NULL,NULL,'active',3,3,NULL,NULL,1,NULL,NULL,NULL),(22,'F000022',NULL,NULL,NULL,1,NULL,NULL,'organization_id',3,1,NULL,NULL,11,NULL,4,28),(23,'F000023',NULL,NULL,NULL,1,NULL,NULL,'order',3,1,NULL,NULL,11,NULL,NULL,NULL),(24,'F000024',NULL,NULL,NULL,1,NULL,NULL,'rows',3,1,NULL,NULL,11,NULL,NULL,NULL),(25,'F000025',NULL,NULL,NULL,1,NULL,NULL,'columns',3,1,NULL,NULL,11,NULL,NULL,NULL),(26,'F000026',NULL,NULL,NULL,1,NULL,NULL,'room_id',3,1,NULL,NULL,11,NULL,9,49),(27,'F000027',NULL,NULL,NULL,1,NULL,NULL,'container_type_id',3,1,NULL,NULL,11,NULL,38,99),(28,'F000028',NULL,NULL,NULL,1,NULL,NULL,'id',4,1,0,1,11,NULL,NULL,NULL),(29,'F000029',NULL,NULL,NULL,1,NULL,NULL,'name',4,2,1,NULL,50,NULL,NULL,NULL),(30,'F000030',NULL,NULL,NULL,1,NULL,NULL,'description',4,2,NULL,NULL,255,NULL,NULL,NULL),(31,'F000031',NULL,NULL,NULL,1,NULL,NULL,'date_created',4,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(32,'F000032',NULL,NULL,NULL,1,NULL,NULL,'last_modified',4,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(33,'F000033',NULL,NULL,NULL,1,NULL,NULL,'active',4,3,NULL,NULL,1,NULL,NULL,NULL),(34,'F000034',NULL,NULL,NULL,1,NULL,NULL,'organization_id',4,1,NULL,NULL,11,NULL,4,28),(35,'F000035',NULL,NULL,NULL,1,NULL,NULL,'order',4,1,NULL,NULL,11,NULL,NULL,NULL),(36,'F000036',NULL,NULL,NULL,1,NULL,NULL,'address_id',4,1,NULL,NULL,11,NULL,1,61),(37,'F000037',NULL,NULL,NULL,1,NULL,NULL,'billing_address_id',4,1,NULL,NULL,11,NULL,1,61),(38,'F000038',NULL,NULL,NULL,1,NULL,NULL,'organization_type_id',4,1,NULL,NULL,11,NULL,5,40),(39,'F000039',NULL,NULL,NULL,1,NULL,NULL,'parent',4,1,NULL,NULL,11,NULL,4,28),(40,'F000040',NULL,NULL,NULL,1,NULL,NULL,'id',5,1,NULL,1,11,NULL,NULL,NULL),(41,'F000041',NULL,NULL,NULL,1,NULL,NULL,'name',5,2,1,NULL,50,NULL,NULL,NULL),(42,'F000042',NULL,NULL,NULL,1,NULL,NULL,'description',5,2,NULL,NULL,255,NULL,NULL,NULL),(43,'F000043',NULL,NULL,NULL,1,NULL,NULL,'date_created',5,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(44,'F000044',NULL,NULL,NULL,1,NULL,NULL,'last_modified',5,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(45,'F000045',NULL,NULL,NULL,1,NULL,NULL,'active',5,3,NULL,NULL,1,NULL,NULL,NULL),(53,'F000053',NULL,NULL,NULL,1,NULL,NULL,'organization_id',5,1,NULL,NULL,11,NULL,4,28),(54,'F000054',NULL,NULL,NULL,1,NULL,NULL,'order',5,1,NULL,NULL,11,NULL,NULL,NULL),(55,'F000055',NULL,NULL,NULL,1,NULL,NULL,'id',8,1,NULL,1,11,NULL,NULL,NULL),(56,'F000056',NULL,NULL,NULL,1,NULL,NULL,'name',8,2,1,NULL,50,NULL,NULL,NULL),(57,'F000057',NULL,NULL,NULL,1,NULL,NULL,'description',8,2,NULL,NULL,255,NULL,NULL,NULL),(58,'F000058',NULL,NULL,NULL,1,NULL,NULL,'date_created',8,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(59,'F000059',NULL,NULL,NULL,1,NULL,NULL,'last_modified',8,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(60,'F000060',NULL,NULL,NULL,1,NULL,NULL,'active',8,3,NULL,NULL,1,NULL,NULL,NULL),(46,'F000046',NULL,NULL,NULL,1,NULL,NULL,'organization_id',8,1,NULL,NULL,11,NULL,4,28),(47,'F000047',NULL,NULL,NULL,1,NULL,NULL,'order',8,1,NULL,NULL,11,NULL,NULL,NULL),(48,'F000048',NULL,NULL,NULL,1,NULL,NULL,'address_id',8,1,NULL,NULL,11,NULL,1,61),(49,'F000049',NULL,NULL,NULL,1,NULL,NULL,'id',9,1,NULL,1,11,NULL,NULL,NULL),(50,'F000050',NULL,NULL,NULL,1,NULL,NULL,'name',9,2,1,NULL,50,NULL,NULL,NULL),(51,'F000051',NULL,NULL,NULL,1,NULL,NULL,'description',9,2,NULL,NULL,255,NULL,NULL,NULL),(52,'F000052',NULL,NULL,NULL,1,NULL,NULL,'date_created',9,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(80,'F000080',NULL,NULL,NULL,1,NULL,NULL,'last_modified',9,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(81,'F000081',NULL,NULL,NULL,1,NULL,NULL,'active',9,3,NULL,NULL,1,NULL,NULL,NULL),(82,'F000082',NULL,NULL,NULL,1,NULL,NULL,'organization_id',9,1,NULL,NULL,11,NULL,4,28),(83,'F000083',NULL,NULL,NULL,1,NULL,NULL,'order',9,1,NULL,NULL,11,NULL,NULL,NULL),(84,'F000084',NULL,NULL,NULL,1,NULL,NULL,'building_id',9,1,NULL,NULL,11,NULL,2,75),(85,'F000085',NULL,NULL,NULL,1,NULL,NULL,'id',10,1,0,1,11,NULL,NULL,NULL),(86,'F000086',NULL,NULL,NULL,1,NULL,NULL,'name',10,2,1,0,50,NULL,NULL,NULL),(1,'F000001',NULL,NULL,NULL,1,NULL,NULL,'description',10,2,0,0,255,NULL,NULL,NULL),(2,'F000002',NULL,NULL,NULL,1,NULL,NULL,'date_created',10,4,0,0,NULL,'datetime.datetime.utcnow',NULL,NULL),(3,'F000003',NULL,NULL,NULL,1,NULL,NULL,'last_modified',10,4,0,0,NULL,'datetime.datetime.utcnow',NULL,NULL),(4,'F000004',NULL,NULL,NULL,1,NULL,NULL,'active',10,3,0,0,1,NULL,NULL,NULL),(5,'F000005',NULL,NULL,NULL,1,NULL,NULL,'organization_id',10,1,NULL,NULL,11,NULL,4,28),(6,'F000006',NULL,NULL,NULL,1,NULL,NULL,'order',10,1,NULL,NULL,11,NULL,NULL,NULL),(7,'F000007',NULL,NULL,NULL,1,NULL,NULL,'password_hash',10,2,0,0,255,NULL,NULL,NULL),(8,'F000008',NULL,NULL,NULL,1,NULL,NULL,'first_name',10,2,0,0,50,NULL,NULL,NULL),(9,'F000009',NULL,NULL,NULL,1,NULL,NULL,'last_name',10,2,0,0,50,NULL,NULL,NULL),(10,'F000010',NULL,NULL,NULL,1,NULL,NULL,'email',10,2,1,0,255,NULL,NULL,NULL),(11,'F000011',NULL,NULL,NULL,1,NULL,NULL,'address_id',10,1,0,0,11,NULL,NULL,NULL),(12,'F000012',NULL,NULL,NULL,1,NULL,NULL,'home_page',10,2,0,0,50,NULL,NULL,NULL),(13,'F000013',NULL,NULL,NULL,1,NULL,NULL,'home_page_variable',10,2,0,0,50,NULL,NULL,NULL),(14,'F000014',NULL,NULL,NULL,1,NULL,NULL,'role_id',10,1,0,0,11,NULL,NULL,NULL),(15,'F000015',NULL,NULL,NULL,1,NULL,NULL,'id',11,1,0,1,11,NULL,NULL,NULL),(16,'F000016',NULL,NULL,NULL,1,NULL,NULL,'name',11,2,1,0,50,NULL,NULL,NULL),(17,'F000017',NULL,NULL,NULL,1,NULL,NULL,'date_created',11,4,0,0,NULL,'datetime.datetime.utcnow',NULL,NULL),(18,'F000018',NULL,NULL,NULL,1,NULL,NULL,'last_modified',11,4,0,0,NULL,'datetime.datetime.utcnow',NULL,NULL),(19,'F000019',NULL,NULL,NULL,1,NULL,NULL,'description',11,2,0,0,255,NULL,NULL,NULL),(20,'F000020',NULL,NULL,NULL,1,NULL,NULL,'active',11,3,0,0,1,NULL,NULL,NULL),(21,'F000021',NULL,NULL,NULL,1,NULL,NULL,'organization_id',10,1,NULL,NULL,11,NULL,4,28),(97,'F000097',NULL,NULL,NULL,1,NULL,NULL,'order',10,1,NULL,NULL,11,NULL,NULL,NULL),(98,'F000098',NULL,NULL,NULL,1,NULL,NULL,'action_value',11,2,0,0,255,NULL,NULL,NULL),(99,'F000099',NULL,NULL,NULL,1,NULL,NULL,'id',38,1,NULL,1,11,NULL,NULL,NULL),(100,'F000100',NULL,NULL,NULL,1,NULL,NULL,'name',38,2,1,NULL,50,NULL,NULL,NULL),(101,'F000101',NULL,NULL,NULL,1,NULL,NULL,'description',38,2,NULL,NULL,255,NULL,NULL,NULL),(102,'F000102',NULL,NULL,NULL,1,NULL,NULL,'date_created',38,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(103,'F000103',NULL,NULL,NULL,1,NULL,NULL,'last_modified',38,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(104,'F000104',NULL,NULL,NULL,1,NULL,NULL,'active',38,3,NULL,NULL,1,NULL,NULL,NULL),(105,'F000105',NULL,NULL,NULL,1,NULL,NULL,'organization_id',10,1,NULL,NULL,11,NULL,4,28),(106,'F000106',NULL,NULL,NULL,1,NULL,NULL,'order',10,1,NULL,NULL,11,NULL,NULL,NULL),(128,'F000128',NULL,NULL,NULL,1,NULL,NULL,'manager',7,3,NULL,NULL,1,NULL,NULL,NULL),(127,'F000127',NULL,NULL,NULL,1,NULL,NULL,'director',7,3,NULL,NULL,1,NULL,NULL,NULL),(117,'F000117',NULL,NULL,NULL,1,NULL,NULL,'id',7,1,NULL,1,11,NULL,NULL,NULL),(118,'F000118',NULL,NULL,NULL,1,NULL,NULL,'name',7,2,1,NULL,50,NULL,NULL,NULL),(119,'F000119',NULL,NULL,NULL,1,NULL,NULL,'description',7,2,NULL,NULL,255,NULL,NULL,NULL),(120,'F000120',NULL,NULL,NULL,1,NULL,NULL,'date_created',7,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(121,'F000121',NULL,NULL,NULL,1,NULL,NULL,'last_modified',7,4,NULL,NULL,NULL,'datetime.datetime.utcnow',NULL,NULL),(122,'F000122',NULL,NULL,NULL,1,NULL,NULL,'active',7,3,NULL,NULL,1,NULL,NULL,NULL),(123,'F000123',NULL,NULL,NULL,1,NULL,NULL,'organization_id',7,1,NULL,NULL,11,NULL,4,28),(124,'F000124',NULL,NULL,NULL,1,NULL,NULL,'order',7,1,NULL,NULL,11,NULL,NULL,NULL),(125,'F000125',NULL,NULL,NULL,1,NULL,NULL,'user_id',7,1,NULL,NULL,11,NULL,10,1),(126,'F000126',NULL,NULL,NULL,1,NULL,NULL,'role_id',7,1,NULL,NULL,11,NULL,6,107);
/*!40000 ALTER TABLE `field` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `field_facility_role`
--

DROP TABLE IF EXISTS `field_facility_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `field_facility_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `facility_role_id` int(11) DEFAULT NULL,
  `field_id` int(11) DEFAULT NULL,
  `display_name` varchar(100) DEFAULT NULL,
  `visible` tinyint(1) DEFAULT NULL,
  `required` tinyint(1) DEFAULT NULL,
  `permission_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `field_id` (`field_id`),
  KEY `permission_id` (`permission_id`),
  KEY `facility_role_id` (`facility_role_id`)
) ENGINE=MyISAM AUTO_INCREMENT=105 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `field_facility_role`
--

LOCK TABLES `field_facility_role` WRITE;
/*!40000 ALTER TABLE `field_facility_role` DISABLE KEYS */;
INSERT INTO `field_facility_role` VALUES (1,'FL000001',NULL,NULL,NULL,1,NULL,1,1,1,'id',1,1,2),(2,'FL000002',NULL,NULL,NULL,1,NULL,2,1,2,'name',1,1,2),(3,'FL000003',NULL,NULL,NULL,1,NULL,3,1,3,'description',1,1,2),(4,'FL000004',NULL,NULL,NULL,1,NULL,4,1,4,'date_created',1,1,2),(5,'FL000005',NULL,NULL,NULL,1,NULL,5,1,5,'last_modified',1,1,2),(6,'FL000006',NULL,NULL,NULL,1,NULL,6,1,6,'active',1,1,2),(7,'FL000007',NULL,NULL,NULL,1,NULL,7,1,7,'password_hash',1,1,2),(8,'FL000008',NULL,NULL,NULL,1,NULL,8,1,8,'first_name',1,1,2),(9,'FL000009',NULL,NULL,NULL,1,NULL,9,1,9,'last_name',1,1,2),(10,'FL000010',NULL,NULL,NULL,1,NULL,10,1,10,'email',1,1,2),(11,'FL000011',NULL,NULL,NULL,1,NULL,11,1,11,'address_id',1,1,2),(12,'FL000012',NULL,NULL,NULL,1,NULL,12,1,12,'home_page',1,1,2),(13,'FL000013',NULL,NULL,NULL,1,NULL,13,1,13,'home_page_variable',1,1,2),(14,'FL000014',NULL,NULL,NULL,1,NULL,14,1,14,'role_id',1,1,2),(15,'FL000015',NULL,NULL,NULL,1,NULL,15,1,15,'id',1,1,2),(16,'FL000016',NULL,NULL,NULL,1,NULL,16,1,16,'name',1,1,2),(17,'FL000017',NULL,NULL,NULL,1,NULL,17,1,17,'date_created',1,1,2),(18,'FL000018',NULL,NULL,NULL,1,NULL,18,1,18,'last_modified',1,1,2),(19,'FL000019',NULL,NULL,NULL,1,NULL,19,1,19,'description',1,1,2),(20,'FL000020',NULL,NULL,NULL,1,NULL,20,1,20,'active',1,1,2),(21,'FL000021',NULL,NULL,NULL,1,NULL,21,1,21,'action_value',1,1,2),(22,'FL000022',NULL,NULL,NULL,1,NULL,22,1,22,'id',1,1,2),(23,'FL000023',NULL,NULL,NULL,1,NULL,23,1,23,'name',1,1,2),(24,'FL000024',NULL,NULL,NULL,1,NULL,24,1,24,'description',1,1,2),(25,'FL000025',NULL,NULL,NULL,1,NULL,25,1,25,'date_created',1,1,2),(26,'FL000026',NULL,NULL,NULL,1,NULL,26,1,26,'last_modified',1,1,2),(27,'FL000027',NULL,NULL,NULL,1,NULL,27,1,27,'active',1,1,2),(28,'FL000028',NULL,NULL,NULL,1,NULL,28,1,28,'address_id',1,1,2),(29,'FL000029',NULL,NULL,NULL,1,NULL,29,1,29,'billing_address_id',1,1,2),(30,'FL000030',NULL,NULL,NULL,1,NULL,30,1,30,'id',1,1,2),(31,'FL000031',NULL,NULL,NULL,1,NULL,31,1,31,'name',1,1,2),(32,'FL000032',NULL,NULL,NULL,1,NULL,32,1,32,'description',1,1,2),(33,'FL000033',NULL,NULL,NULL,1,NULL,33,1,33,'date_created',1,1,2),(34,'FL000034',NULL,NULL,NULL,1,NULL,34,1,34,'last_modified',1,1,2),(35,'FL000035',NULL,NULL,NULL,1,NULL,35,1,35,'active',1,1,2),(36,'FL000036',NULL,NULL,NULL,1,NULL,36,1,36,'organization_id',1,1,2),(37,'FL000037',NULL,NULL,NULL,1,NULL,37,1,37,'institution_id',1,1,2),(38,'FL000038',NULL,NULL,NULL,1,NULL,38,1,38,'id',1,1,2),(39,'FL000039',NULL,NULL,NULL,1,NULL,39,1,39,'name',1,1,2),(40,'FL000040',NULL,NULL,NULL,1,NULL,40,1,40,'description',1,1,2),(41,'FL000041',NULL,NULL,NULL,1,NULL,41,1,41,'date_created',1,1,2),(42,'FL000042',NULL,NULL,NULL,1,NULL,42,1,42,'last_modified',1,1,2),(43,'FL000043',NULL,NULL,NULL,1,NULL,43,1,43,'active',1,1,2),(44,'FL000044',NULL,NULL,NULL,1,NULL,44,1,44,'organization_id',1,1,2),(45,'FL000045',NULL,NULL,NULL,1,NULL,45,1,45,'user_id',1,1,2),(46,'FL000046',NULL,NULL,NULL,1,NULL,46,1,46,'id',1,1,2),(47,'FL000047',NULL,NULL,NULL,1,NULL,47,1,47,'name',1,1,2),(48,'FL000048',NULL,NULL,NULL,1,NULL,48,1,48,'description',1,1,2),(49,'FL000049',NULL,NULL,NULL,1,NULL,49,1,49,'date_created',1,1,2),(50,'FL000050',NULL,NULL,NULL,1,NULL,50,1,50,'last_modified',1,1,2),(51,'FL000051',NULL,NULL,NULL,1,NULL,51,1,51,'active',1,1,2),(52,'FL000052',NULL,NULL,NULL,1,NULL,52,1,52,'address_id',1,1,2),(53,'FL000053',NULL,NULL,NULL,1,NULL,53,1,53,'id',1,1,2),(54,'FL000054',NULL,NULL,NULL,1,NULL,54,1,54,'name',1,1,2),(55,'FL000055',NULL,NULL,NULL,1,NULL,55,1,55,'description',1,1,2),(56,'FL000056',NULL,NULL,NULL,1,NULL,56,1,56,'date_created',1,1,2),(57,'FL000057',NULL,NULL,NULL,1,NULL,57,1,57,'last_modified',1,1,2),(58,'FL000058',NULL,NULL,NULL,1,NULL,58,1,58,'active',1,1,2),(59,'FL000059',NULL,NULL,NULL,1,NULL,59,1,59,'organization_id',1,1,2),(60,'FL000060',NULL,NULL,NULL,1,NULL,60,1,60,'user_id',1,1,2),(61,'FL000061',NULL,NULL,NULL,1,NULL,61,1,61,'id',1,1,2),(62,'FL000062',NULL,NULL,NULL,1,NULL,62,1,62,'name',1,1,2),(63,'FL000063',NULL,NULL,NULL,1,NULL,63,1,63,'description',1,1,2),(64,'FL000064',NULL,NULL,NULL,1,NULL,64,1,64,'date_created',1,1,2),(65,'FL000065',NULL,NULL,NULL,1,NULL,65,1,65,'last_modified',1,1,2),(66,'FL000066',NULL,NULL,NULL,1,NULL,66,1,66,'active',1,1,2),(67,'FL000067',NULL,NULL,NULL,1,NULL,67,1,67,'address_1',1,1,2),(68,'FL000068',NULL,NULL,NULL,1,NULL,68,1,68,'address_2',1,1,2),(69,'FL000069',NULL,NULL,NULL,1,NULL,69,1,69,'city',1,1,2),(70,'FL000070',NULL,NULL,NULL,1,NULL,70,1,70,'state',1,1,2),(71,'FL000071',NULL,NULL,NULL,1,NULL,71,1,71,'postcode',1,1,2),(72,'FL000072',NULL,NULL,NULL,1,NULL,72,1,72,'country',1,1,2),(73,'FL000073',NULL,NULL,NULL,1,NULL,73,1,73,'id',1,1,2),(74,'FL000074',NULL,NULL,NULL,1,NULL,74,1,74,'name',1,1,2),(75,'FL000075',NULL,NULL,NULL,1,NULL,75,1,75,'description',1,1,2),(76,'FL000076',NULL,NULL,NULL,1,NULL,76,1,76,'date_created',1,1,2),(77,'FL000077',NULL,NULL,NULL,1,NULL,77,1,77,'last_modified',1,1,2),(78,'FL000078',NULL,NULL,NULL,1,NULL,78,1,78,'active',1,1,2),(79,'FL000079',NULL,NULL,NULL,1,NULL,79,1,79,'address_id',1,1,2),(80,'FL000080',NULL,NULL,NULL,1,NULL,80,1,80,'id',1,1,2),(81,'FL000081',NULL,NULL,NULL,1,NULL,81,1,81,'name',1,1,2),(82,'FL000082',NULL,NULL,NULL,1,NULL,82,1,82,'description',1,1,2),(83,'FL000083',NULL,NULL,NULL,1,NULL,83,1,83,'date_created',1,1,2),(84,'FL000084',NULL,NULL,NULL,1,NULL,84,1,84,'last_modified',1,1,2),(85,'FL000085',NULL,NULL,NULL,1,NULL,85,1,85,'active',1,1,2),(86,'FL000086',NULL,NULL,NULL,1,NULL,86,1,86,'building_id',1,1,2),(87,'FL000087',NULL,NULL,NULL,1,NULL,87,1,87,'id',1,1,2),(88,'FL000088',NULL,NULL,NULL,1,NULL,88,1,88,'name',1,1,2),(89,'FL000089',NULL,NULL,NULL,1,NULL,89,1,89,'description',1,1,2),(90,'FL000090',NULL,NULL,NULL,1,NULL,90,1,90,'date_created',1,1,2),(91,'FL000091',NULL,NULL,NULL,1,NULL,91,1,91,'last_modified',1,1,2),(92,'FL000092',NULL,NULL,NULL,1,NULL,92,1,92,'active',1,1,2),(93,'FL000093',NULL,NULL,NULL,1,NULL,93,1,93,'rows',1,1,2),(94,'FL000094',NULL,NULL,NULL,1,NULL,94,1,94,'columns',1,1,2),(95,'FL000095',NULL,NULL,NULL,1,NULL,95,1,95,'room_id',1,1,2),(96,'FL000096',NULL,NULL,NULL,1,NULL,96,1,96,'container_type_id',1,1,2),(97,'FL000097',NULL,NULL,NULL,1,NULL,97,1,97,'id',1,1,2),(98,'FL000098',NULL,NULL,NULL,1,NULL,98,1,98,'name',1,1,2),(99,'FL000099',NULL,NULL,NULL,1,NULL,99,1,99,'description',1,1,2),(100,'FL000100',NULL,NULL,NULL,1,NULL,100,1,100,'date_created',1,1,2),(101,'FL000101',NULL,NULL,NULL,1,NULL,101,1,101,'last_modified',1,1,2),(102,'FL000102',NULL,NULL,NULL,1,NULL,102,1,102,'active',1,1,2),(103,'FL000103',NULL,NULL,NULL,1,NULL,103,1,127,'director',1,1,2),(104,'FL000104',NULL,NULL,NULL,1,NULL,104,1,128,'manager',1,1,2);
/*!40000 ALTER TABLE `field_facility_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `menu_type_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `menu_type_id` (`menu_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu`
--

LOCK TABLES `menu` WRITE;
/*!40000 ALTER TABLE `menu` DISABLE KEYS */;
INSERT INTO `menu` VALUES (1,'AdminBanner','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,2),(2,'AdminSideMenu','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,1);
/*!40000 ALTER TABLE `menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_facility_role`
--

DROP TABLE IF EXISTS `menu_facility_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu_facility_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `facility_role_id` int(11) DEFAULT NULL,
  `menu_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `menu_id` (`menu_id`),
  KEY `facility_role_id` (`facility_role_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_facility_role`
--

LOCK TABLES `menu_facility_role` WRITE;
/*!40000 ALTER TABLE `menu_facility_role` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu_facility_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_item`
--

DROP TABLE IF EXISTS `menu_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `menu_item_value` varchar(250) DEFAULT NULL,
  `menu_id` int(11) DEFAULT NULL,
  `page_form_id` int(11) DEFAULT NULL,
  `parameter` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `menu_id` (`menu_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_item`
--

LOCK TABLES `menu_item` WRITE;
/*!40000 ALTER TABLE `menu_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_item_facility_role`
--

DROP TABLE IF EXISTS `menu_item_facility_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu_item_facility_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `facility_role_id` int(11) DEFAULT NULL,
  `menu_item_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `menu_item_id` (`menu_item_id`),
  KEY `facility_role_id` (`facility_role_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_item_facility_role`
--

LOCK TABLES `menu_item_facility_role` WRITE;
/*!40000 ALTER TABLE `menu_item_facility_role` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu_item_facility_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_type`
--

DROP TABLE IF EXISTS `menu_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_type`
--

LOCK TABLES `menu_type` WRITE;
/*!40000 ALTER TABLE `menu_type` DISABLE KEYS */;
INSERT INTO `menu_type` VALUES (1,'SideBar','Side Bar','0000-00-00 00:00:00','0000-00-00 00:00:00',1),(2,'NavigationBar','Navigation Bar','0000-00-00 00:00:00','0000-00-00 00:00:00',1);
/*!40000 ALTER TABLE `menu_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `module`
--

DROP TABLE IF EXISTS `module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `module` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `module`
--

LOCK TABLES `module` WRITE;
/*!40000 ALTER TABLE `module` DISABLE KEYS */;
INSERT INTO `module` VALUES (2,'mod_lab',NULL,NULL,NULL,1,NULL,NULL),(3,'mod_auth',NULL,NULL,NULL,1,NULL,NULL),(4,'mod_admin',NULL,NULL,NULL,1,NULL,NULL),(5,'mod_api',NULL,NULL,NULL,1,NULL,NULL);
/*!40000 ALTER TABLE `module` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `new_user`
--

DROP TABLE IF EXISTS `new_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `new_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `password_hash` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `institution` varchar(100) DEFAULT NULL,
  `address1` varchar(100) DEFAULT NULL,
  `address2` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `postcode` varchar(100) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `pi` varchar(100) DEFAULT NULL,
  `group` varchar(100) DEFAULT NULL,
  `server` varchar(100) DEFAULT NULL,
  `directory` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `new_user`
--

LOCK TABLES `new_user` WRITE;
/*!40000 ALTER TABLE `new_user` DISABLE KEYS */;
INSERT INTO `new_user` VALUES (1,'test',NULL,'2015-08-31 14:13:55','2015-08-31 14:13:55',0,NULL,NULL,'test','test','pbkdf2:sha1:1000$l9mPeihb$da7501c015b8264612f9e00b1a61b2868157d074','test@test.com','test','test','','test','test','test','+16715551212','test','test',NULL,NULL),(2,'test test',NULL,'2015-08-31 18:04:17','2015-08-31 18:04:17',0,NULL,NULL,'test','test','pbkdf2:sha1:1000$UQFMWK5T$445ac09aa060695052232946f2b890696be066e1','test@test.com','test','test','','test','test','test','+16715551212','test','test','iggybase',NULL),(3,'testy',NULL,'2015-08-31 18:17:01','2015-08-31 18:17:01',0,NULL,NULL,'test','test','pbkdf2:sha1:1000$kiOOs667$ca1ad6a408d8638e22411cc9ebb4c63f9eb1410a','test@test.com','test','test','','test','test','test','8005551212','test','test','iggybase',NULL);
/*!40000 ALTER TABLE `new_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_form`
--

DROP TABLE IF EXISTS `page_form`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_form` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `page_title` varchar(50) DEFAULT NULL,
  `page_header` varchar(50) DEFAULT NULL,
  `page_template` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_form`
--

LOCK TABLES `page_form` WRITE;
/*!40000 ALTER TABLE `page_form` DISABLE KEYS */;
INSERT INTO `page_form` VALUES (1,'mod_core/summary',NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,'mod_core/summary.html'),(2,'index',NULL,NULL,NULL,1,NULL,NULL,'Iggybase','Iggybase','mod_auth/msgform.html'),(3,'mod_auth/failedlogin',NULL,NULL,NULL,1,NULL,NULL,'Iggybase - Login Failed','Login Failed','mod_auth/msgform.html'),(4,'mod_auth/login',NULL,NULL,NULL,1,NULL,NULL,'Iggybase - Login','Login','mod_auth/entryform.html'),(5,'mod_auth/regcomplete',NULL,NULL,NULL,1,NULL,NULL,'Iggybase','Registering Complete','mod_auth/msgform.html'),(6,'mod_auth/register',NULL,NULL,NULL,1,NULL,NULL,'Iggybase - Register','Register','mod_auth/entryform.html'),(7,'mod_auth/regerror',NULL,NULL,NULL,1,NULL,NULL,'Iggybase','Registering Error','mod_auth/msgform.html');
/*!40000 ALTER TABLE `page_form` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_form_button`
--

DROP TABLE IF EXISTS `page_form_button`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_form_button` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `page_form_id` int(11) DEFAULT NULL,
  `button_type` varchar(100) DEFAULT NULL,
  `button_class` varchar(100) DEFAULT NULL,
  `button_value` varchar(100) DEFAULT NULL,
  `button_id` varchar(100) DEFAULT NULL,
  `special_props` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_form_button`
--

LOCK TABLES `page_form_button` WRITE;
/*!40000 ALTER TABLE `page_form_button` DISABLE KEYS */;
INSERT INTO `page_form_button` VALUES (1,'B000001',NULL,NULL,NULL,1,NULL,NULL,4,'submit','btn btn-default','Login','login',NULL),(2,'B000002',NULL,NULL,NULL,1,NULL,NULL,4,'button','btn btn-default','Register','login_register',NULL),(3,'B000003',NULL,NULL,NULL,1,NULL,NULL,6,'submit','btn btn-default','Register','register',NULL),(4,'B000004',NULL,NULL,NULL,1,NULL,NULL,3,'button','btn btn-default','Login','regcompletelogin',NULL),(5,'B000005',NULL,NULL,NULL,1,NULL,NULL,3,'button','btn btn-default','Register','login_register',NULL),(6,'B000006',NULL,NULL,NULL,1,NULL,NULL,5,'button','btn btn-default','Login','regcompletelogin',NULL),(7,'B000007',NULL,NULL,NULL,1,NULL,NULL,7,'button','btn btn-default','Login','regcompletelogin',NULL),(8,'B000008',NULL,NULL,NULL,1,NULL,NULL,7,'button','btn btn-default','Register','login_register',NULL);
/*!40000 ALTER TABLE `page_form_button` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_form_button_facility_role`
--

DROP TABLE IF EXISTS `page_form_button_facility_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_form_button_facility_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `facility_role_id` int(11) DEFAULT NULL,
  `page_form_button_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `facility_role_id` (`facility_role_id`),
  KEY `page_form_button_id` (`page_form_button_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_form_button_facility_role`
--

LOCK TABLES `page_form_button_facility_role` WRITE;
/*!40000 ALTER TABLE `page_form_button_facility_role` DISABLE KEYS */;
INSERT INTO `page_form_button_facility_role` VALUES (1,'BR000001',NULL,NULL,NULL,1,NULL,NULL,1,1),(2,'BR000002',NULL,NULL,NULL,1,NULL,NULL,1,2),(3,'BR000003',NULL,NULL,NULL,1,NULL,NULL,2,1),(4,'BR000004',NULL,NULL,NULL,1,NULL,NULL,1,3),(5,'BR000005',NULL,NULL,NULL,1,NULL,NULL,1,4),(6,'BR000006',NULL,NULL,NULL,1,NULL,NULL,1,5),(7,'BR000007',NULL,NULL,NULL,1,NULL,NULL,1,6),(8,'BR000008',NULL,NULL,NULL,1,NULL,NULL,1,7),(9,'BR000009',NULL,NULL,NULL,1,NULL,NULL,1,8);
/*!40000 ALTER TABLE `page_form_button_facility_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_form_facility_role`
--

DROP TABLE IF EXISTS `page_form_facility_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_form_facility_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `facility_role_id` int(11) DEFAULT NULL,
  `page_form_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `page_form_id` (`page_form_id`),
  KEY `facility_role_id` (`facility_role_id`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_form_facility_role`
--

LOCK TABLES `page_form_facility_role` WRITE;
/*!40000 ALTER TABLE `page_form_facility_role` DISABLE KEYS */;
INSERT INTO `page_form_facility_role` VALUES (1,'PR000001',NULL,NULL,NULL,1,NULL,NULL,1,1),(2,'PR000002',NULL,NULL,NULL,1,NULL,NULL,1,2),(3,'PR000003',NULL,NULL,NULL,1,NULL,NULL,1,3),(4,'PR000004',NULL,NULL,NULL,1,NULL,NULL,1,4),(5,'PR000005',NULL,NULL,NULL,1,NULL,NULL,1,5),(6,'PR000006',NULL,NULL,NULL,1,NULL,NULL,1,6),(7,'PR000007',NULL,NULL,NULL,1,NULL,NULL,1,7);
/*!40000 ALTER TABLE `page_form_facility_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_form_javascript`
--

DROP TABLE IF EXISTS `page_form_javascript`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_form_javascript` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `page_form_id` int(11) DEFAULT NULL,
  `page_javascript` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `page_form_id` (`page_form_id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_form_javascript`
--

LOCK TABLES `page_form_javascript` WRITE;
/*!40000 ALTER TABLE `page_form_javascript` DISABLE KEYS */;
INSERT INTO `page_form_javascript` VALUES (1,'PJ000001',NULL,NULL,NULL,1,NULL,NULL,3,'mod_auth/main.js'),(2,'PJ000002',NULL,NULL,NULL,1,NULL,NULL,4,'mod_auth/main.js'),(3,'PJ000003',NULL,NULL,NULL,1,NULL,NULL,5,'mod_auth/main.js'),(4,'PJ000004',NULL,NULL,NULL,1,NULL,NULL,6,'mod_auth/main.js'),(5,'PJ000005',NULL,NULL,NULL,1,NULL,NULL,7,'mod_auth/main.js');
/*!40000 ALTER TABLE `page_form_javascript` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permission`
--

DROP TABLE IF EXISTS `permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permission`
--

LOCK TABLES `permission` WRITE;
/*!40000 ALTER TABLE `permission` DISABLE KEYS */;
INSERT INTO `permission` VALUES (1,'read_only','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL),(2,'write','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL);
/*!40000 ALTER TABLE `permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'Admin',NULL,NULL,NULL,1,NULL,NULL),(2,'CoreUser',NULL,NULL,NULL,1,NULL,NULL),(3,'User',NULL,NULL,NULL,1,NULL,NULL),(4,'ReadOnly',NULL,NULL,NULL,1,NULL,NULL),(5,'LabAdmin',NULL,NULL,NULL,1,NULL,NULL),(6,'CoreManager',NULL,NULL,NULL,1,NULL,NULL);
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_object`
--

DROP TABLE IF EXISTS `table_object`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_object` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `new_name_prefix` varchar(100) DEFAULT NULL,
  `new_name_id` int(11) DEFAULT NULL,
  `id_length` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `new_name_prefix` (`new_name_prefix`)
) ENGINE=MyISAM AUTO_INCREMENT=39 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_object`
--

LOCK TABLES `table_object` WRITE;
/*!40000 ALTER TABLE `table_object` DISABLE KEYS */;
INSERT INTO `table_object` VALUES (1,'address','address table','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'AD',0,6),(2,'building','building table','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'BD',0,6),(3,'container','Container table','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'CT',0,6),(4,'organization','organization table, controls data access','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'OR',0,6),(5,'organization_type','an organization type table','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'OT',0,6),(7,'user_role','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,NULL,NULL,NULL),(8,'institution','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'IS',0,6),(9,'room','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'RM',0,6),(10,'user','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,NULL,NULL,NULL),(11,'action','action','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'AC',0,6),(12,'action_group_role','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'AL',0,6),(13,'field','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,NULL,NULL,NULL),(14,'field_group_role','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'FL',0,6),(15,'sample','','0000-00-00 00:00:00','0000-00-00 00:00:00',0,NULL,NULL,'S',0,6),(16,'lab','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,NULL,NULL,NULL),(17,'group_role','functional security table','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'GR',0,6),(18,'menu','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'MN',0,6),(19,'menu_item','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'MI',0,6),(20,'menu_item_group_role','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'MR',0,6),(21,'menu_group_role','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'ML',0,6),(22,'menu_type','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'MT',0,6),(23,'new_user','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,NULL,NULL,NULL),(24,'page','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,NULL,NULL,NULL),(25,'page_group_role','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'PL',0,6),(26,'permission','read write access','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,NULL,NULL,NULL),(27,'role','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,NULL,NULL,NULL),(28,'table_object','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,NULL,NULL,NULL),(29,'table_object_group_role','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'TL',0,6),(33,'project','','0000-00-00 00:00:00','0000-00-00 00:00:00',0,NULL,NULL,'P',0,6),(31,'table_query','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'TQ',0,6),(32,'table_query_types','','0000-00-00 00:00:00','0000-00-00 00:00:00',1,NULL,NULL,'TT',0,6),(34,'study','','0000-00-00 00:00:00','0000-00-00 00:00:00',0,NULL,NULL,'ST',0,6),(35,'oligo','','0000-00-00 00:00:00','0000-00-00 00:00:00',0,NULL,NULL,'O',0,6),(36,'batch','','0000-00-00 00:00:00','0000-00-00 00:00:00',0,NULL,NULL,'B',0,6),(37,'batch_items','','0000-00-00 00:00:00','0000-00-00 00:00:00',0,NULL,NULL,'BI',0,6),(38,'container_type',NULL,NULL,NULL,1,NULL,NULL,'CE',0,6);
/*!40000 ALTER TABLE `table_object` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_object_facility_role`
--

DROP TABLE IF EXISTS `table_object_facility_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_object_facility_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `facility_role_id` int(11) DEFAULT NULL,
  `table_object_id` int(11) DEFAULT NULL,
  `module_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `table_object_id` (`table_object_id`),
  KEY `facility_role_id` (`facility_role_id`)
) ENGINE=MyISAM AUTO_INCREMENT=39 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_object_facility_role`
--

LOCK TABLES `table_object_facility_role` WRITE;
/*!40000 ALTER TABLE `table_object_facility_role` DISABLE KEYS */;
INSERT INTO `table_object_facility_role` VALUES (1,'TL000001',NULL,NULL,NULL,1,NULL,NULL,1,1,2),(2,'TL000002',NULL,NULL,NULL,1,NULL,NULL,1,2,2),(3,'TL000003',NULL,NULL,NULL,1,NULL,NULL,1,3,2),(4,'TL000004',NULL,NULL,NULL,1,NULL,NULL,1,4,2),(5,'TL000005',NULL,NULL,NULL,1,NULL,NULL,1,5,2),(7,'TL000007',NULL,NULL,NULL,1,NULL,NULL,1,7,3),(8,'TL000008',NULL,NULL,NULL,1,NULL,NULL,1,8,2),(9,'TL000009',NULL,NULL,NULL,1,NULL,NULL,1,9,2),(10,'TL000010',NULL,NULL,NULL,1,NULL,NULL,1,10,3),(11,'TL000011',NULL,NULL,NULL,1,NULL,NULL,1,11,4),(12,'TL000012',NULL,NULL,NULL,1,NULL,NULL,1,12,4),(13,'TL000013',NULL,NULL,NULL,1,NULL,NULL,1,13,4),(14,'TL000014',NULL,NULL,NULL,1,NULL,NULL,1,14,4),(15,'TL000015',NULL,NULL,NULL,1,NULL,NULL,1,15,2),(16,'TL000016',NULL,NULL,NULL,1,NULL,NULL,1,16,4),(17,'TL000017',NULL,NULL,NULL,1,NULL,NULL,1,17,4),(18,'TL000018',NULL,NULL,NULL,1,NULL,NULL,1,18,4),(19,'TL000019',NULL,NULL,NULL,1,NULL,NULL,1,19,4),(20,'TL000020',NULL,NULL,NULL,1,NULL,NULL,1,20,4),(21,'TL000021',NULL,NULL,NULL,1,NULL,NULL,1,21,4),(22,'TL000022',NULL,NULL,NULL,1,NULL,NULL,1,22,4),(23,'TL000023',NULL,NULL,NULL,1,NULL,NULL,1,23,4),(24,'TL000024',NULL,NULL,NULL,1,NULL,NULL,1,24,4),(25,'TL000025',NULL,NULL,NULL,1,NULL,NULL,1,25,4),(26,'TL000026',NULL,NULL,NULL,1,NULL,NULL,1,26,4),(27,'TL000027',NULL,NULL,NULL,1,NULL,NULL,1,27,4),(28,'TL000028',NULL,NULL,NULL,1,NULL,NULL,1,28,4),(29,'TL000029',NULL,NULL,NULL,1,NULL,NULL,1,29,4),(31,'TL000031',NULL,NULL,NULL,1,NULL,NULL,1,31,4),(32,'TL000032',NULL,NULL,NULL,1,NULL,NULL,1,32,4),(33,'TL000033',NULL,NULL,NULL,1,NULL,NULL,1,33,2),(34,'TL000034',NULL,NULL,NULL,1,NULL,NULL,1,34,2),(35,'TL000035',NULL,NULL,NULL,1,NULL,NULL,1,35,2),(36,'TL000036',NULL,NULL,NULL,1,NULL,NULL,1,36,2),(37,'TL000037',NULL,NULL,NULL,1,NULL,NULL,1,37,2),(38,'TL000038',NULL,NULL,NULL,1,NULL,NULL,1,38,2);
/*!40000 ALTER TABLE `table_object_facility_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_query`
--

DROP TABLE IF EXISTS `table_query`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_query` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_query`
--

LOCK TABLES `table_query` WRITE;
/*!40000 ALTER TABLE `table_query` DISABLE KEYS */;
/*!40000 ALTER TABLE `table_query` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_query_criteria`
--

DROP TABLE IF EXISTS `table_query_criteria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_query_criteria` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `table_query_id` int(11) DEFAULT NULL,
  `criteria` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `table_query_id` (`table_query_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_query_criteria`
--

LOCK TABLES `table_query_criteria` WRITE;
/*!40000 ALTER TABLE `table_query_criteria` DISABLE KEYS */;
/*!40000 ALTER TABLE `table_query_criteria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_query_field`
--

DROP TABLE IF EXISTS `table_query_field`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_query_field` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `table_query_id` int(11) DEFAULT NULL,
  `field_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `table_query_id` (`table_query_id`),
  KEY `field_id` (`field_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_query_field`
--

LOCK TABLES `table_query_field` WRITE;
/*!40000 ALTER TABLE `table_query_field` DISABLE KEYS */;
/*!40000 ALTER TABLE `table_query_field` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_query_order`
--

DROP TABLE IF EXISTS `table_query_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_query_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `table_query_id` int(11) DEFAULT NULL,
  `field_id` int(11) DEFAULT NULL,
  `direction` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `table_query_id` (`table_query_id`),
  KEY `field_id` (`field_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_query_order`
--

LOCK TABLES `table_query_order` WRITE;
/*!40000 ALTER TABLE `table_query_order` DISABLE KEYS */;
/*!40000 ALTER TABLE `table_query_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_query_type`
--

DROP TABLE IF EXISTS `table_query_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_query_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `organization_id` int(11) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `table_query_id` int(11) DEFAULT NULL,
  `table_object_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `table_query_id` (`table_query_id`),
  KEY `table_object_id` (`table_object_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_query_type`
--

LOCK TABLES `table_query_type` WRITE;
/*!40000 ALTER TABLE `table_query_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `table_query_type` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-05 15:02:47
