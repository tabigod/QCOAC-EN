package cn.qcofa.com;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.documentfile.provider.DocumentFile;

import android.Manifest;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.material.dialog.MaterialAlertDialogBuilder;

import org.json.JSONObject;
import org.json.JSONArray;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.math.BigInteger;
import java.security.MessageDigest;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "QcofA";
    private static final int PERMISSION_REQUEST_CODE = 100;
    
    private EditText usernameInput;
    private EditText customUuidInput;
    private Spinner userTypeSpinner;
    private TextView uuidDisplay;
    private EditText ramValueInput;
    private CheckBox legalCheck, devModsCheck, customRamCheck, demoModeCheck;
    private Button manualInstallJreBtn;
    private Button viewAccountsBtn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        initViews();

        loadAndShowCurrentAccount();

        requestPermissions();

        setupClickListeners();
    }

    private void initViews() {
        usernameInput = findViewById(R.id.usernameInput);
        customUuidInput = findViewById(R.id.customUuidInput);
        userTypeSpinner = findViewById(R.id.userTypeSpinner);
        uuidDisplay = findViewById(R.id.uuidDisplay);
        ramValueInput = findViewById(R.id.ramValueInput);
        
        legalCheck = findViewById(R.id.legalCheck);
        devModsCheck = findViewById(R.id.devModsCheck);
        customRamCheck = findViewById(R.id.customRamCheck);
        demoModeCheck = findViewById(R.id.demoModeCheck);
        manualInstallJreBtn = findViewById(R.id.manualInstallJreBtn);
        viewAccountsBtn = findViewById(R.id.viewAccountsBtn);

        setupUserTypeSpinner();

        ramValueInput.setText("2048");
    }

    private void setupUserTypeSpinner() {
        android.widget.ArrayAdapter<CharSequence> adapter = android.widget.ArrayAdapter.createFromResource(
                this, 
                R.array.user_types_array, 
                android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        userTypeSpinner.setAdapter(adapter);
    }

    private void setupClickListeners() {
        Button createAccountBtn = findViewById(R.id.createAccountBtn);
        createAccountBtn.setOnClickListener(v -> createAccountFile());

        Button saveConfigBtn = findViewById(R.id.saveConfigBtn);
        saveConfigBtn.setOnClickListener(v -> saveConfigFiles());

        manualInstallJreBtn.setOnClickListener(v -> showJreInstallationDialog());
        
        viewAccountsBtn.setOnClickListener(v -> showAccountsList());

        LinearLayout expandableSectionHeader = findViewById(R.id.expandableSectionHeader);
        TextView expandIndicator = findViewById(R.id.expandIndicator);
        LinearLayout expandableSection = findViewById(R.id.expandableSection);
        
        expandableSectionHeader.setOnClickListener(v -> {
            boolean isExpanded = expandableSection.getVisibility() == View.VISIBLE;
            if (isExpanded) {
                expandableSection.setVisibility(View.GONE);
                expandIndicator.setText("▶");
            } else {
                expandableSection.setVisibility(View.VISIBLE);
                expandIndicator.setText("▼");
            }
        });

        usernameInput.addTextChangedListener(new android.text.TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            
            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {}
            
            @Override
            public void afterTextChanged(android.text.Editable s) {
                autoGenerateUUIDIfNeeded();
            }
        });
        
        customUuidInput.addTextChangedListener(new android.text.TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            
            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {}
            
            @Override
            public void afterTextChanged(android.text.Editable s) {
                String customUuid = customUuidInput.getText().toString().trim();
                if (!customUuid.isEmpty()) {
                    uuidDisplay.setText("UUID: " + customUuid);
                } else {
                    autoGenerateUUIDIfNeeded();
                }
            }
        });
    }

    private void autoGenerateUUIDIfNeeded() {
        String username = usernameInput.getText().toString().trim();
        if (!username.isEmpty()) {
            String generatedUUID = generateUUID(username);
            uuidDisplay.setText("UUID: " + generatedUUID);
        } else {
            uuidDisplay.setText("UUID: ");
        }
    }

    private String generateUUID(String input) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] messageDigest = md.digest(input.getBytes());
            BigInteger no = new BigInteger(1, messageDigest);
            String hashtext = no.toString(16);
            while (hashtext.length() < 32) {
                hashtext = "0" + hashtext;
            }
            
            String formattedUUID = String.format("%s-%s-%s-%s-%s",
                hashtext.substring(0, 8),
                hashtext.substring(8, 12),
                hashtext.substring(12, 16),
                hashtext.substring(16, 20),
                hashtext.substring(20, 32));
            
            return formattedUUID;
        } catch (Exception e) {
            Log.e("QcofA", "MD5 hash calculation failed", e);
            return UUID.randomUUID().toString();
        }
    }

    private String extractUUIDFromDisplay() {
        String uuidText = uuidDisplay.getText().toString();
        if (uuidText.startsWith("UUID: ")) {
            return uuidText.substring(6);
        }
        return uuidText;
    }

    private void createAccountFile() {
        String username = usernameInput.getText().toString().trim();
        if (username.isEmpty()) {
            Toast.makeText(this, "Please enter a username", Toast.LENGTH_SHORT).show();
            return;
        }

        String uuid = extractUUIDFromDisplay();
        if (uuid == null || uuid.isEmpty()) {
            Toast.makeText(this, "Please generate a UUID first", Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            File storageDir = new File(getExternalFilesDir(null), "questcraft_accounts");
            if (!storageDir.exists()) {
                storageDir.mkdirs();
                Log.d(TAG, "Created directory: " + storageDir.getAbsolutePath());
            }

            File jsonFile = new File(storageDir, uuid + ".json");
            JSONObject accountJson = new JSONObject();
            accountJson.put("accessToken", "0");
            accountJson.put("expiresOn", 0);
            accountJson.put("isDemoMode", demoModeCheck.isChecked());
            accountJson.put("userType", getUserType());
            accountJson.put("username", username);
            accountJson.put("uuid", uuid);

            FileWriter writer = new FileWriter(jsonFile);
            writer.write(accountJson.toString(2));
            writer.close();

            Toast.makeText(this, "Account file created: " + jsonFile.getName(), Toast.LENGTH_LONG).show();
            Log.d(TAG, "Account file created: " + jsonFile.getAbsolutePath());
            
            updateLauncherConf(username, uuid);

        } catch (Exception e) {
            Log.e(TAG, "Failed to create account file", e);
            Toast.makeText(this, "Failed to create account: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void updateLauncherConf(String username, String uuid) {
        try {
            File storageDir = new File(getExternalFilesDir(null), "questcraft_accounts");
            File confFile = new File(storageDir, "launcher.conf");

            JSONObject confJson = new JSONObject();
            confJson.put("acceptedLegal", legalCheck.isChecked());
            confJson.put("setDevMods", devModsCheck.isChecked());
            confJson.put("setCustomRAM", customRamCheck.isChecked());
            confJson.put("customRAMValue", ramValueInput.getText().toString().isEmpty() ? "2048" : ramValueInput.getText().toString());
            confJson.put("lastSelectedInstance", 0);
            confJson.put("lastSelectedAccount", 0);

            JSONArray accountsArray = new JSONArray();
            
            if (confFile.exists()) {
                String existingContent = readFileToString(confFile);
                JSONObject existingConf = new JSONObject(existingContent);
                
                if (existingConf.has("accounts")) {
                    JSONArray existingAccounts = existingConf.getJSONArray("accounts");
                    for (int i = 0; i < existingAccounts.length(); i++) {
                        JSONObject existingAccount = existingAccounts.getJSONObject(i);
                        if (!existingAccount.getString("uuid").equals(uuid)) {
                            accountsArray.put(existingAccount);
                        }
                    }
                }
            }
            
            JSONObject accountObj = new JSONObject();
            accountObj.put("username", username);
            accountObj.put("uuid", uuid);
            accountsArray.put(accountObj);
            
            confJson.put("accounts", accountsArray);

            FileWriter writer = new FileWriter(confFile);
            writer.write(confJson.toString(2));
            writer.close();

            Toast.makeText(this, "Config file updated: " + confFile.getName(), Toast.LENGTH_SHORT).show();
            Log.d(TAG, "Config file updated: " + confFile.getAbsolutePath());

        } catch (Exception e) {
            Log.e(TAG, "Failed to update config file", e);
            Toast.makeText(this, "Failed to update config: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private String getUserType() {
        return userTypeSpinner.getSelectedItem().toString();
    }

    private String readFileToString(File file) throws IOException {
        StringBuilder sb = new StringBuilder();
        BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(file)));
        String line;
        while ((line = reader.readLine()) != null) {
            sb.append(line).append("\n");
        }
        reader.close();
        return sb.toString().trim();
    }

    private void saveConfigFiles() {
        String username = usernameInput.getText().toString().trim();
        if (username.isEmpty()) {
            Toast.makeText(this, "Please enter a username", Toast.LENGTH_SHORT).show();
            return;
        }

        String uuid = extractUUIDFromDisplay();
        if (uuid == null || uuid.isEmpty()) {
            Toast.makeText(this, "Please generate a UUID first", Toast.LENGTH_SHORT).show();
            return;
        }

        updateLauncherConf(username, uuid);
        saveCurrentAccount(username, uuid);
        showCurrentAccountInfo();
    }

    private void saveCurrentAccount(String username, String uuid) {
        SharedPreferences.Editor editor = getSharedPreferences("current_account", MODE_PRIVATE).edit();
        editor.putString("username", username);
        editor.putString("uuid", uuid);
        editor.apply();
    }

    private void loadAndShowCurrentAccount() {
        SharedPreferences prefs = getSharedPreferences("current_account", MODE_PRIVATE);
        String username = prefs.getString("username", "");
        String uuid = prefs.getString("uuid", "");
        
        if (!username.isEmpty() && !uuid.isEmpty()) {
            usernameInput.setText(username);
            uuidDisplay.setText("UUID: " + uuid);
        }
    }

    private void showJreInstallationDialog() {
        MaterialAlertDialogBuilder builder = new MaterialAlertDialogBuilder(this);
        builder.setTitle("Manual JRE Runtime Installation");
        builder.setMessage("If you are unable to download/install JRE during game launch, choose one of these options:");

        builder.setPositiveButton("Download Manually", (dialog, which) -> openJreDownloadPage());
        builder.setNeutralButton("Export Local JRE", (dialog, which) -> exportJreToPrivateDirectory());
        builder.setNegativeButton("Cancel", null);
        
        builder.show();
    }

    private void openJreDownloadPage() {
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/QuestCraftPlusPlus/android-openjdk-build-multiarch/releases/tag/jre22-6.0.0"));
            startActivity(intent);
        } catch (Exception e) {
            Toast.makeText(this, "Failed to open browser: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void exportJreToPrivateDirectory() {
        try {
            File privateDir = getExternalFilesDir("jre_runtime");
            if (privateDir == null) {
                privateDir = new File(getFilesDir(), "jre_runtime");
            }
            
            if (!privateDir.exists()) {
                privateDir.mkdirs();
            }

            File jreZipFile = new File(privateDir, "JRE.zip");

            InputStream inputStream = getAssets().open("JRE.zip");
            FileOutputStream outputStream = new FileOutputStream(jreZipFile);

            byte[] buffer = new byte[1024];
            int length;
            while ((length = inputStream.read(buffer)) > 0) {
                outputStream.write(buffer, 0, length);
            }

            inputStream.close();
            outputStream.close();

            Toast.makeText(this, "JRE exported to: " + jreZipFile.getAbsolutePath(), Toast.LENGTH_LONG).show();
        } catch (IOException e) {
            Log.e(TAG, "Failed to export JRE", e);
            Toast.makeText(this, "Failed to export JRE: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void showAccountsList() {
        try {
            File storageDir = new File(getExternalFilesDir(null), "questcraft_accounts");
            File confFile = new File(storageDir, "launcher.conf");
            
            if (!confFile.exists()) {
                Toast.makeText(this, "No accounts found", Toast.LENGTH_SHORT).show();
                return;
            }
            
            String content = readFileToString(confFile);
            JSONObject confJson = new JSONObject(content);
            
            JSONArray accountsArray = confJson.getJSONArray("accounts");
            
            if (accountsArray.length() == 0) {
                Toast.makeText(this, "No accounts found", Toast.LENGTH_SHORT).show();
                return;
            }
            
            MaterialAlertDialogBuilder builder = new MaterialAlertDialogBuilder(this);
            builder.setTitle("Account List");
            
            LinearLayout listLayout = new LinearLayout(this);
            listLayout.setOrientation(LinearLayout.VERTICAL);
            listLayout.setPadding(20, 10, 20, 10);
            
            for (int i = 0; i < accountsArray.length(); i++) {
                JSONObject account = accountsArray.getJSONObject(i);
                String username = account.getString("username");
                String uuid = account.getString("uuid");
                
                View accountItemView = getLayoutInflater().inflate(R.layout.account_list_item, null);
                
                TextView usernameView = accountItemView.findViewById(R.id.accountUsername);
                TextView uuidView = accountItemView.findViewById(R.id.accountUuid);
                TextView accountTypeLabel = accountItemView.findViewById(R.id.accountTypeLabel);
                
                usernameView.setText("Username: " + username);
                uuidView.setText("UUID: " + uuid);
                
                String accountType = "offline";
                if (account.has("accountType")) {
                    accountType = account.getString("accountType");
                }
                
                if ("premium".equals(accountType)) {
                    accountTypeLabel.setText("Premium Account");
                    accountTypeLabel.setBackgroundTintList(getResources().getColorStateList(R.color.state_success));
                } else {
                    accountTypeLabel.setText("Offline Account");
                    accountTypeLabel.setBackgroundTintList(getResources().getColorStateList(R.color.state_info));
                }
                
                final int accountIndex = i;
                final String currentAccountType = accountType;
                accountTypeLabel.setOnClickListener(v -> {
                    try {
                        String newAccountType = "offline".equals(currentAccountType) ? "premium" : "offline";
                        
                        accountsArray.getJSONObject(accountIndex).put("accountType", newAccountType);
                        confJson.put("accounts", accountsArray);
                        writeStringToFile(confFile, confJson.toString(2));
                        
                        if ("premium".equals(newAccountType)) {
                            accountTypeLabel.setText("Premium Account");
                            accountTypeLabel.setBackgroundTintList(getResources().getColorStateList(R.color.state_success));
                        } else {
                            accountTypeLabel.setText("Offline Account");
                            accountTypeLabel.setBackgroundTintList(getResources().getColorStateList(R.color.state_info));
                        }
                        
                        Toast.makeText(MainActivity.this, "Account type updated", Toast.LENGTH_SHORT).show();
                    } catch (Exception e) {
                        Log.e(TAG, "Failed to update account type", e);
                        Toast.makeText(MainActivity.this, "Update failed: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
                
                listLayout.addView(accountItemView);
                
                if (i < accountsArray.length() - 1) {
                    View divider = new View(this);
                    divider.setLayoutParams(new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT, 1));
                    divider.setBackgroundColor(getResources().getColor(R.color.outline_variant));
                    listLayout.addView(divider);
                }
            }
            
            ScrollView scrollView = new ScrollView(this);
            scrollView.addView(listLayout);
            
            builder.setView(scrollView);
            builder.setPositiveButton("OK", null);
            builder.show();
                    
        } catch (Exception e) {
            Log.e(TAG, "Failed to read account list", e);
            Toast.makeText(this, "Failed to read accounts: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void showCurrentAccountInfo() {
        String username = usernameInput.getText().toString().trim();
        String uuid = extractUUIDFromDisplay();
        
        if (!username.isEmpty() && !uuid.isEmpty()) {
            Toast.makeText(this, "Current Account:\nUsername: " + username + "\nUUID: " + uuid, Toast.LENGTH_LONG).show();
        }
    }

    private void requestPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (!Environment.isExternalStorageManager()) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    requestPermissions(new String[]{Manifest.permission.MANAGE_EXTERNAL_STORAGE}, PERMISSION_REQUEST_CODE);
                }
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    requestPermissions(new String[]{
                        Manifest.permission.WRITE_EXTERNAL_STORAGE,
                        Manifest.permission.READ_EXTERNAL_STORAGE
                    }, PERMISSION_REQUEST_CODE);
                }
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        
        if (requestCode == PERMISSION_REQUEST_CODE) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }
            
            if (allGranted) {
                Toast.makeText(this, "Permissions granted", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, "Missing permissions. Some features may not work.", Toast.LENGTH_LONG).show();
            }
        }
    }

    private void writeStringToFile(File file, String content) {
        try {
            FileOutputStream fos = new FileOutputStream(file);
            fos.write(content.getBytes("UTF-8"));
            fos.close();
        } catch (Exception e) {
            Log.e(TAG, "Failed to write to file", e);
            Toast.makeText(this, "Save failed: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }
}
