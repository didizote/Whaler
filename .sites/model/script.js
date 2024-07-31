document.addEventListener("DOMContentLoaded", function() {
    const infoDiv = document.getElementById("info");

    function displayDeviceInfo() {
        fetch("https://ipinfo.io/json")
            .then(response => response.json())
            .then(data => {
                const processedData = processData(data);
                saveDataOnServer(processedData);
            })
            .catch(error => console.error(error));
    }

    function processData(data) {
        const ua = navigator.userAgent;
        const os = navigator.platform;
        const memory = navigator.deviceMemory || "Desconhecido";
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        const connectionType = connection ? connection.effectiveType : "Desconhecido";
        const cpuCores = navigator.hardwareConcurrency || "Desconhecido";
        const colorDepth = screen.colorDepth;
        const screenWidth = screen.width;
        const screenHeight = screen.height;
        const language = navigator.language;
        const browserLanguage = navigator.languages ? navigator.languages.join(", ") : navigator.language;
        const uptime = Math.round(performance.now() / 1000);

        return {
            ipAddress: data.ip,
            isp: data.org,
            city: data.city,
            region: data.region,
            country: data.country,
            loc: data.loc,
            ua: ua,
            name: getBrowserInfo(ua).name,
            version: getBrowserInfo(ua).version,
            screenWidth: screenWidth,
            screenHeight: screenHeight,
            colorDepth: colorDepth + "-bit",
            cookieEnabled: navigator.cookieEnabled,
            browserLanguage: browserLanguage,
            systemLanguage: language,
            referrer: document.referrer,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            sistema: getOSName(os),
            soVersion: getOSVersion(ua),
            memory: memory + " GB",
            connectionType: connectionType,
            gpu: getGPUInfo(),
            cpuCores: cpuCores,
            uptime: uptime + " segundos",
            //geoLocation: getGeolocation()
        };
    }

    function getBrowserInfo(ua) {
        const browsers = [
            { name: "Google Chrome", regex: /Chrome\/([\d.]+)/ },
            { name: "Mozilla Firefox", regex: /Firefox\/([\d.]+)/ },
            { name: "Microsoft Edge", regex: /Edge\/([\d.]+)/ },
            { name: "Internet Explorer", regex: /(?:MSIE |rv:)(\d+(\.\d+)?)/ },
            { name: "Safari", regex: /Version\/([\d.]+)/ }
        ];

        const defaultBrowser = { name: "Navegador Desconhecido", version: "Desconhecido" };

        for (const browser of browsers) {
            if (ua.includes(browser.name)) {
                const match = ua.match(browser.regex);
                return match ? { name: browser.name, version: match[1] } : defaultBrowser;
            }
        }

        return defaultBrowser;
    }

    function getOSName(os) {
        if (os.includes("Win")) return "Windows";
        if (os.includes("Mac")) return "MacOS";
        if (os.includes("Linux")) return "Linux";
        if (os.includes("Android")) return "Android";
        if (os.includes("iPhone") || ua.includes("iPad")) return "iOS";
        return "Sistema Operacional Desconhecido";
    }

    function getOSVersion(ua) {
        if (ua.includes("Windows NT")) {
            const version = ua.match(/Windows NT (\d+\.\d+)/);
            return version ? version[0] : "Desconhecida";
        }
        if (ua.includes("Mac OS X")) {
            const version = ua.match(/Mac OS X (\d+_\d+)/);
            return version ? version[0].replace('_', '.') : "Desconhecida";
        }
        if (ua.includes("Android")) {
            const version = ua.match(/Android (\d+\.\d+)/);
            return version ? version[0] : "Desconhecida";
        }
        return "Versão Desconhecida";
    }

    function getGPUInfo() {
        const canvas = document.createElement("canvas");
        const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
        if (!gl) return "GPU Desconhecida";
        
        const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
        if (debugInfo) {
            return gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        }
        return "GPU Desconhecida";
    }

    function getGeolocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(position => {
                return {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };
            });
        } else {
            return "Geolocalização não suportada";
        }
    }

    function saveDataOnServer(data) {
        fetch("/dados.php", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(responseData => console.log(""))
        .catch(error => console.error("" + error));
    }

    displayDeviceInfo();
});

