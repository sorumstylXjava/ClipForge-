# Retrofit & Gson - fix ParameterizedType error
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.clipforge.data.remote.api.** { *; }
-keep class com.clipforge.domain.model.** { *; }
-keepclassmembers,allowobfuscation class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

# Google Credential Manager
-if class androidx.credentials.CredentialManager
-keep class androidx.credentials.** { *; }
-keep class com.google.android.libraries.identity.googleid.** { *; }
