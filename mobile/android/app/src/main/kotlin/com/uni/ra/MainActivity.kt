package com.uni.ra

import android.content.pm.PackageManager
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.embedding.android.FlutterActivity
import io.flutter.plugin.common.MethodChannel

class MainActivity: FlutterActivity() {
  private val channelName = "app/google_maps_config"

  override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
    super.configureFlutterEngine(flutterEngine)

    MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channelName)
      .setMethodCallHandler { call, result ->
        when (call.method) {
          "getGoogleMapsApiKey" -> result.success(getGoogleMapsApiKey())
          else -> result.notImplemented()
        }
      }
  }

  private fun getGoogleMapsApiKey(): String? {
    val appInfo = packageManager.getApplicationInfo(packageName, PackageManager.GET_META_DATA)
    val metaData = appInfo.metaData
    return metaData?.getString("com.google.android.geo.API_KEY")
  }
}
