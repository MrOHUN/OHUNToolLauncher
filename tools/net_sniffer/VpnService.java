// net_sniffer/VpnService.java

package com.ohun.netsniffer;

import android.content.Intent;
import android.net.VpnService;
import android.os.ParcelFileDescriptor;
import android.util.Log;

public class NetSnifferVpnService extends VpnService {

    private static final String TAG = "NetSnifferVpn";
    private ParcelFileDescriptor vpnInterface = null;
    private static NetSnifferVpnService instance = null;

    // Python tarafidan chaqiriladi
    public static NetSnifferVpnService getInstance() {
        return instance;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
        Log.d(TAG, "VpnService yaratildi");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        startVpn();
        return START_STICKY;
    }

    private void startVpn() {
        try {
            Builder builder = new Builder();
            builder.setSession("NetSniffer");
            builder.addAddress("10.0.0.1", 32);
            builder.addRoute("0.0.0.0", 0);  // barcha trafik
            builder.addDnsServer("8.8.8.8");
            builder.setMtu(65535);
            vpnInterface = builder.establish();

            if (vpnInterface != null) {
                Log.d(TAG, "VPN interfeysi ochildi, fd: " + vpnInterface.getFd());
                // Python ga fd yuborish
                notifyPython(vpnInterface.getFd());
            }
        } catch (Exception e) {
            Log.e(TAG, "VPN xato: " + e.getMessage());
        }
    }

    // Python Pyjnius orqali shu metodini chaqiradi
    public int getFd() {
        if (vpnInterface != null) {
            return vpnInterface.getFd();
        }
        return -1;
    }

    private void notifyPython(int fd) {
        // Pyjnius orqali Python callback chaqiriladi
        Log.d(TAG, "Python ga fd yuborildi: " + fd);
    }

    public void stopVpn() {
        try {
            if (vpnInterface != null) {
                vpnInterface.close();
                vpnInterface = null;
            }
            stopSelf();
        } catch (Exception e) {
            Log.e(TAG, "Stop xato: " + e.getMessage());
        }
    }

    @Override
    public void onDestroy() {
        stopVpn();
        instance = null;
        super.onDestroy();
    }
}