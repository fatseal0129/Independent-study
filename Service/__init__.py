import Service.DatabaseService
import Service.FileService
import Service.AlertService
import Service.CameraService
import Service.SendServerService

DBService = DatabaseService.DatabaseService()
FileService = FileService
AlertService = AlertService
CameraManager = CameraService.CameraManager()
ServerManager = SendServerService.sendService()
