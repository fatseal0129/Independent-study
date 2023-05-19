import Server.Service.DatabaseService
import Server.Service.FileService
import Server.Service.AlertService
import Server.Service.DetectService

DB = DatabaseService.DatabaseService()
FileManager = FileService
AlertManager = AlertService.AlertSUS()
DetectManager = DetectService.DetectManager()