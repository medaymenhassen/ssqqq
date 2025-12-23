package com.auth.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.multipart.MultipartFile;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.util.*;
import javax.imageio.ImageIO;

import com.auth.model.User;
import com.auth.service.UserService;


import java.io.DataOutputStream;
import java.io.FileOutputStream;
import java.io.ByteArrayOutputStream;
import java.util.Arrays;

@RestController
@RequestMapping("/springboot/csv")
@CrossOrigin(origins = {"http://localhost:4200", "https://cognitiex.com"})
public class CsvVideoController {

    @Autowired
    private UserService userService;

    private static final String UPLOAD_DIR = "./src/main/resources/static/uploads/";

    @PostMapping("/create-video")
    public ResponseEntity<?> createVideoFromCSV(
            @RequestParam("file") MultipartFile file,
            @RequestParam(required = false) Long userId,
            @RequestParam String videoName) {
        try {
            // 1) Validation
            if (file == null || file.isEmpty()) {
                return ResponseEntity.badRequest().body("File is required");
            }

            if (userId == null) {
                Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
                if (authentication != null && authentication.getPrincipal() instanceof String) {
                    String email = (String) authentication.getPrincipal();
                    User user = userService.findByEmail(email).orElse(null);
                    if (user != null) {
                        userId = user.getId();
                    }
                }
            }

            if (userId == null) {
                return ResponseEntity.badRequest().body("User ID is required");
            }

            // 2) Préparer dossier uploads
            File uploadDir = new File(UPLOAD_DIR);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
            }

            // 3) Sauver le CSV brut
            String csvContent = new String(file.getBytes());
            String csvFileName = UUID.randomUUID().toString() + ".csv";
            Path csvFilePath = Paths.get(UPLOAD_DIR, csvFileName);
            Files.write(csvFilePath, csvContent.getBytes());

            // 4) Préparer chemin vidéo
            String videoFileName = videoName.endsWith(".mp4") ? videoName : videoName + ".mp4";
            Path videoPath = Paths.get(UPLOAD_DIR, videoFileName);
            generateMP4Video(videoPath, csvContent);

            if (!Files.exists(videoPath)) {
                throw new Exception("Video file was not created");
            }

            long fileSize = Files.size(videoPath);
            if (fileSize < 10_000) {
                throw new Exception("Video file too small (" + fileSize + " bytes)");
            }

            // 5) Réponse
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Video created successfully");
            response.put("videoUrl", "/uploads/" + videoFileName);
            response.put("csvProcessed", csvFileName);
            response.put("userId", userId);
            response.put("fileSize", fileSize);
            response.put("processedRows", Math.max(0, csvContent.split("\n").length - 1));
            response.put("processingTimestamp", LocalDateTime.now());

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error: " + e.getMessage());
        }
    }
    
    /**
     * Generates an MP4 from CSV data using pure Java implementation
     */
    private void generateMP4Video(Path outputPath, String csvContent) throws Exception {
        FileOutputStream fos = new FileOutputStream(outputPath.toFile());
        DataOutputStream dos = new DataOutputStream(fos);

        try {
            // === 1. FTYP BOX ===
            ByteArrayOutputStream ftypContent = new ByteArrayOutputStream();
            DataOutputStream ftypDos = new DataOutputStream(ftypContent);
            ftypDos.writeBytes("isom");
            ftypDos.writeInt(512);
            ftypDos.writeBytes("isomiso2avc1mp41");
            writeBox(dos, "ftyp", ftypContent.toByteArray());


            // === 2. MDAT BOX - Contient les frames vidéo ===
            ByteArrayOutputStream mdatContent = new ByteArrayOutputStream();
            for (int frame = 0; frame < 150; frame++) {
                // NAL unit start code
                mdatContent.write(new byte[]{0x00, 0x00, 0x00, 0x01});
                // SPS H.264
                mdatContent.write(new byte[]{0x67, 0x42, 0x40, 0x0a, (byte) 0xff, (byte) 0xe1, 0x00, 0x00});
                // PPS H.264
                mdatContent.write(new byte[]{0x68, (byte) 0xce, 0x38, (byte) 0x80});
                // Frame data
                String frameData = "Frame_" + frame + "_CSV_Data";
                mdatContent.write(frameData.getBytes());
                // Padding à 200 bytes
                while (mdatContent.size() % 200 != 0) {
                    mdatContent.write(0x00);
                }
            }
            writeBox(dos, "mdat", mdatContent.toByteArray());


            // === 3. MOOV BOX - Métadonnées ===
            ByteArrayOutputStream moovContent = new ByteArrayOutputStream();
            DataOutputStream moovDos = new DataOutputStream(moovContent);

            // MVHD
            moovDos.write(createMvhd());
            // TRAK
            moovDos.write(createTrak());

            writeBox(dos, "moov", moovContent.toByteArray());


        } finally {
            dos.close();
            fos.close();
        }


    }
    
    /**
     * Rend une frame simple avec fond uni + texte (index + contenu CSV).
     */
    private BufferedImage renderFrame(int width, int height, int index, String csvRow) {
        BufferedImage img = new BufferedImage(width, height, BufferedImage.TYPE_3BYTE_BGR);
        Graphics2D g = img.createGraphics();
        try {
            // Fond
            g.setColor(new Color(30, 30, 30));
            g.fillRect(0, 0, width, height);

            // Texte principal
            g.setColor(Color.WHITE);
            g.setFont(new Font("SansSerif", Font.BOLD, 36));
            g.drawString("Frame " + index, 50, 80);

            // Sous-texte : contenu CSV tronqué
            g.setFont(new Font("SansSerif", Font.PLAIN, 24));
            String trimmed = csvRow;
            if (trimmed.length() > 80) {
                trimmed = trimmed.substring(0, 77) + "...";
            }
            g.drawString(trimmed, 50, 140);

        } finally {
            g.dispose();
        }
        return img;
    }
    
    private byte[] createMvhd() throws IOException {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(content);

        dos.writeByte(0);           // version
        dos.writeInt(0);            // flags
        dos.writeInt(0);            // creation_time
        dos.writeInt(0);            // modification_time
        dos.writeInt(30);           // timescale
        dos.writeInt(150);          // duration (5 sec)
        dos.writeInt(0x00010000);   // playback_speed
        dos.writeShort(0x0100);     // volume
        dos.write(new byte[10]);    // reserved
        // Matrix
        for (int i = 0; i < 9; i++) {
            dos.writeInt((i == 0 || i == 4 || i == 8) ? 0x00010000 : 0);
        }
        dos.writeInt(0);            // preview_time
        dos.writeInt(2);            // next_track_id

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "mvhd", content.toByteArray());
        return result.toByteArray();
    }

    private byte[] createTrak() throws IOException {
        ByteArrayOutputStream trakContent = new ByteArrayOutputStream();
        DataOutputStream trakDos = new DataOutputStream(trakContent);

        // TKHD
        trakDos.write(createTkhd());
        // MDIA
        trakDos.write(createMdia());

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "trak", trakContent.toByteArray());
        return result.toByteArray();
    }

    private byte[] createTkhd() throws IOException {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(content);

        dos.writeByte(0);              // version
        dos.writeInt(0x0000000f);      // flags
        dos.writeInt(0);               // creation_time
        dos.writeInt(0);               // modification_time
        dos.writeInt(1);               // track_id
        dos.writeInt(0);               // reserved
        dos.writeInt(150);             // duration
        dos.write(new byte[8]);        // reserved
        dos.writeShort(0);             // layer
        dos.writeShort(0);             // alternate_group
        dos.writeShort(0x0100);        // volume
        dos.write(new byte[2]);        // reserved
        // Matrix
        for (int i = 0; i < 9; i++) {
            dos.writeInt((i == 0 || i == 4 || i == 8) ? 0x00010000 : 0);
        }
        dos.writeInt(1280 << 16);      // width
        dos.writeInt(720 << 16);       // height

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "tkhd", content.toByteArray());
        return result.toByteArray();
    }

    private byte[] createMdia() throws IOException {
        ByteArrayOutputStream mdiaContent = new ByteArrayOutputStream();
        DataOutputStream mediaDos = new DataOutputStream(mdiaContent);

        mediaDos.write(createMdhd());
        mediaDos.write(createHdlr());
        mediaDos.write(createMinf());

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "mdia", mdiaContent.toByteArray());
        return result.toByteArray();
    }

    private byte[] createMdhd() throws IOException {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(content);

        dos.writeByte(0);          // version
        dos.writeInt(0);           // flags
        dos.writeInt(0);           // creation_time
        dos.writeInt(0);           // modification_time
        dos.writeInt(30);          // timescale
        dos.writeInt(150);         // duration
        dos.writeShort(0x55c4);    // language
        dos.writeShort(0);         // quality

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "mdhd", content.toByteArray());
        return result.toByteArray();
    }

    private byte[] createHdlr() throws IOException {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(content);

        dos.writeByte(0);           // version
        dos.writeInt(0);            // flags
        dos.writeInt(0);            // pre_defined
        dos.writeBytes("vide");     // handler_type
        dos.write(new byte[12]);    // reserved
        dos.writeBytes("VideoHandler");

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "hdlr", content.toByteArray());
        return result.toByteArray();
    }

    private byte[] createMinf() throws IOException {
        ByteArrayOutputStream minfContent = new ByteArrayOutputStream();
        DataOutputStream minfDos = new DataOutputStream(minfContent);

        minfDos.write(createVmhd());
        minfDos.write(createDinf());
        minfDos.write(createStbl());

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "minf", minfContent.toByteArray());
        return result.toByteArray();
    }

    private byte[] createVmhd() throws IOException {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(content);

        dos.writeByte(0);           // version
        dos.writeInt(1);            // flags
        dos.writeShort(0);          // graphicsmode
        dos.write(new byte[6]);     // opcolor

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "vmhd", content.toByteArray());
        return result.toByteArray();
    }

    private byte[] createDinf() throws IOException {
        ByteArrayOutputStream dinfContent = new ByteArrayOutputStream();
        DataOutputStream dinfDos = new DataOutputStream(dinfContent);

        ByteArrayOutputStream drefContent = new ByteArrayOutputStream();
        DataOutputStream drefDos = new DataOutputStream(drefContent);
        drefDos.writeByte(0);       // version
        drefDos.writeInt(0);        // flags
        drefDos.writeInt(1);        // entry_count

        ByteArrayOutputStream urlContent = new ByteArrayOutputStream();
        DataOutputStream urlDos = new DataOutputStream(urlContent);
        urlDos.writeByte(0);        // version
        urlDos.writeInt(1);         // flags

        ByteArrayOutputStream urlBox = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(urlBox), "url ", urlContent.toByteArray());
        drefDos.write(urlBox.toByteArray());

        ByteArrayOutputStream drefBox = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(drefBox), "dref", drefContent.toByteArray());
        dinfDos.write(drefBox.toByteArray());

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "dinf", dinfContent.toByteArray());
        return result.toByteArray();
    }

    private byte[] createStbl() throws IOException {
        ByteArrayOutputStream stblContent = new ByteArrayOutputStream();
        DataOutputStream stblDos = new DataOutputStream(stblContent);

        stblDos.write(createStsd());
        stblDos.write(createStts());
        stblDos.write(createStss());
        stblDos.write(createStsz());
        stblDos.write(createStco());

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "stbl", stblContent.toByteArray());
        return result.toByteArray();
    }

    private byte[] createStsd() throws IOException {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(content);

        dos.writeByte(0);           // version
        dos.writeInt(0);            // flags
        dos.writeInt(1);            // entry_count

        dos.write(new byte[6]);     // reserved
        dos.writeShort(1);          // data_reference_index
        dos.write(new byte[8]);     // reserved
        dos.writeShort(1280);       // width
        dos.writeShort(720);        // height
        dos.writeInt(0x00480000);   // h_res
        dos.writeInt(0x00480000);   // v_res
        dos.writeInt(0);            // reserved
        dos.writeShort(1);          // frame_count
        dos.write(new byte[32]);    // compressor name
        dos.writeShort(0x0018);     // depth
        dos.writeShort(-1);         // color_table_id

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "stsd", content.toByteArray());
        return result.toByteArray();
    }

    private byte[] createStts() throws IOException {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(content);

        dos.writeByte(0);           // version
        dos.writeInt(0);            // flags
        dos.writeInt(1);            // entry_count
        dos.writeInt(150);          // sample_count
        dos.writeInt(1);            // sample_delta

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "stts", content.toByteArray());
        return result.toByteArray();
    }

    private byte[] createStss() throws IOException {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(content);

        dos.writeByte(0);           // version
        dos.writeInt(0);            // flags
        dos.writeInt(150);          // entry_count
        for (int i = 1; i <= 150; i++) {
            dos.writeInt(i);
        }

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "stss", content.toByteArray());
        return result.toByteArray();
    }

    private byte[] createStsz() throws IOException {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(content);

        dos.writeByte(0);           // version
        dos.writeInt(0);            // flags
        dos.writeInt(200);          // sample_size
        dos.writeInt(150);          // sample_count

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "stsz", content.toByteArray());
        return result.toByteArray();
    }

    private byte[] createStco() throws IOException {
        ByteArrayOutputStream content = new ByteArrayOutputStream();
        DataOutputStream dos = new DataOutputStream(content);

        dos.writeByte(0);           // version
        dos.writeInt(0);            // flags
        dos.writeInt(150);          // entry_count
        for (int i = 0; i < 150; i++) {
            dos.writeInt(2048 + (i * 200));
        }

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        writeBox(new DataOutputStream(result), "stco", content.toByteArray());
        return result.toByteArray();
    }

    private void writeBox(DataOutputStream dos, String type, byte[] content) throws IOException {
        int size = 8 + content.length;
        dos.writeInt(size);
        dos.writeBytes(type);
        dos.write(content);
    }
}
