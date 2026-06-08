import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material';
import 'package:http/http.as_http' as http;
import 'package:image_picker/image_picker.dart';

// Model to represent parsed business card data
class BusinessCardData {
  final String? ownerName;
  final String? designation;
  final String? companyName;
  final String? email;
  final String? website;
  final String? location;
  final List<String> phones;

  BusinessCardData({
    this.ownerName,
    this.designation,
    this.companyName,
    this.email,
    this.website,
    this.location,
    required this.phones,
  });

  factory BusinessCardData.fromJson(Map<String, dynamic> json) {
    return BusinessCardData(
      ownerName: json['owner_name'],
      designation: json['designation'],
      companyName: json['company_name'],
      email: json['email'],
      website: json['website'],
      location: json['location'],
      phones: List<String>.from(json['phones'] ?? []),
    );
  }
}

class BusinessCardScanner extends StatefulWidget {
  // Replace with your FastAPI OCR service endpoint URL
  // Use http://10.0.2.2:8000 for Android Emulator to access host's localhost
  // Use http://localhost:8000 for iOS simulator, Flutter Web, or Desktop
  final String apiUrl;

  const BusinessCardScanner({
    super.key,
    this.apiUrl = "http://10.0.2.2:8000/extract-text",
  });

  @override
  State<BusinessCardScanner> createState() => _BusinessCardScannerState();
}

class _BusinessCardScannerState extends State<BusinessCardScanner> {
  final ImagePicker _picker = ImagePicker();
  
  XFile? _selectedFile;
  Uint8List? _imageBytes;
  bool _isLoading = false;
  String? _errorMessage;
  
  String? _rawText;
  BusinessCardData? _parsedData;

  // Pick an image using image_picker (works on Web, Android, iOS, macOS, Windows)
  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? image = await _picker.pickImage(
        source: source,
        maxWidth: 1800,
        maxHeight: 1800,
        imageQuality: 85, // Pre-compress for faster upload
      );

      if (image != null) {
        final bytes = await image.readAsBytes();
        setState(() {
          _selectedFile = image;
          _imageBytes = bytes;
          _errorMessage = null;
          _rawText = null;
          _parsedData = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = "Failed to select image: $e";
      });
    }
  }

  // Upload the image as bytes to FastAPI to support both Web and Mobile
  Future<void> _uploadAndExtract() async {
    if (_imageBytes == null || _selectedFile == null) {
      setState(() {
        _errorMessage = "Please select an image first.";
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // Create Multipart Request
      final uri = Uri.parse(widget.apiUrl);
      final request = http.MultipartRequest('POST', uri);

      // Create multipart file from bytes (essential for Flutter Web compatibility)
      final multipartFile = http.MultipartFile.fromBytes(
        'file',
        _imageBytes!,
        filename: _selectedFile!.name,
      );

      request.files.add(multipartFile);

      // Send Request
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final Map<String, dynamic> jsonResponse = json.decode(response.body);
        if (jsonResponse['success'] == true) {
          setState(() {
            _rawText = jsonResponse['text'];
            _parsedData = BusinessCardData.fromJson(jsonResponse['parsed_data']);
          });
        } else {
          setState(() {
            _errorMessage = "Extraction was unsuccessful on server.";
          });
        }
      } else {
        final Map<String, dynamic> errJson = json.decode(response.body);
        final String detail = errJson['detail'] ?? "Server error: ${response.statusCode}";
        setState(() {
          _errorMessage = detail;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = "Network request failed: $e";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Business Card OCR Parser"),
        centerTitle: true,
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image Preview Card
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Container(
                height: 220,
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: _imageBytes != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.memory(_imageBytes!, fit: BoxFit.contain),
                      )
                    : const Center(
                        child: Icon(Icons.add_a_photo_outlined, size: 50, color: Colors.grey),
                      ),
              ),
            ),
            const SizedBox(height: 16),

            // Source Selector Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.teal[50]),
                    icon: const Icon(Icons.photo_library, color: Colors.teal),
                    label: const Text("Gallery", style: TextStyle(color: Colors.teal)),
                    onPressed: () => _pickImage(ImageSource.gallery),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.teal[50]),
                    icon: const Icon(Icons.camera_alt, color: Colors.teal),
                    label: const Text("Camera", style: TextStyle(color: Colors.teal)),
                    onPressed: () => _pickImage(ImageSource.camera),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Extract Button
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.teal,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              onPressed: _isLoading ? null : _uploadAndExtract,
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                    )
                  : const Text("Extract & Parse Card", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(height: 16),

            // Error Display
            if (_errorMessage != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red[200]!),
                ),
                child: Text(
                  _errorMessage!,
                  style: const TextStyle(color: Colors.red),
                  textAlign: TextAlign.center,
                ),
              ),

            // Structured Results Panel
            if (_parsedData != null) ...[
              const Text(
                "Parsed Card Details",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.teal),
              ),
              const SizedBox(height: 8),
              Card(
                elevation: 3,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      _buildInfoTile(Icons.person, "Name", _parsedData!.ownerName),
                      _buildInfoTile(Icons.badge, "Designation", _parsedData!.designation),
                      _buildInfoTile(Icons.business, "Company Name", _parsedData!.companyName),
                      _buildInfoTile(Icons.email, "Email", _parsedData!.email),
                      _buildInfoTile(Icons.language, "Website", _parsedData!.website),
                      _buildInfoTile(Icons.location_on, "Location/Address", _parsedData!.location),
                      _buildInfoTile(
                        Icons.phone, 
                        "Phones", 
                        _parsedData!.phones.isNotEmpty ? _parsedData!.phones.join(", ") : null
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Raw OCR Output Panel (Expandable)
            if (_rawText != null) ...[
              ExpansionTile(
                title: const Text("View Raw OCR Text"),
                textColor: Colors.teal,
                iconColor: Colors.teal,
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      _rawText!,
                      style: const TextStyle(fontFamily: 'Courier', fontSize: 13),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoTile(IconData icon, String label, String? value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: Colors.teal[700], size: 22),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey, fontWeight: FontWeight.w500)),
                const SizedBox(height: 2),
                Text(
                  value ?? "Not found",
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: value != null ? FontWeight.w600 : FontWeight.normal,
                    color: value != null ? Colors.black87 : Colors.grey[500],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
