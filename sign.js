// TikTok Live Signature Generator
// 抖音直播签名生成器

// 模拟浏览器环境
var document = {
    createElement: function(tag) {
        return {
            style: {},
            setAttribute: function() {},
            getAttribute: function() { return null; },
            appendChild: function() {},
            removeChild: function() {}
        };
    },
    getElementsByTagName: function() {
        return [];
    },
    getElementById: function() {
        return null;
    },
    body: {
        appendChild: function() {},
        removeChild: function() {}
    }
};

var window = {
    document: document,
    navigator: {
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    },
    location: {
        href: 'https://live.douyin.com/',
        protocol: 'https:',
        host: 'live.douyin.com'
    },
    screen: {
        width: 1920,
        height: 1080
    },
    Date: Date,
    Math: Math,
    parseInt: parseInt,
    parseFloat: parseFloat,
    encodeURIComponent: encodeURIComponent,
    decodeURIComponent: decodeURIComponent
};

var navigator = window.navigator;

// 混淆的签名生成函数
function w_0x25f3(_0x4a8c5b, _0x3f4d28) {
    var _0x25f3a4 = [
        'charCodeAt', 'length', 'toString', 'substr', 'split',
        'join', 'replace', 'indexOf', 'slice', 'push',
        'pop', 'shift', 'unshift', 'reverse', 'sort',
        'concat', 'toLowerCase', 'toUpperCase', 'match',
        'search', 'test', 'exec', 'apply', 'call'
    ];
    
    var _0x4a8c = function(_0x25f3a4, _0x3f4d28) {
        _0x25f3a4 = _0x25f3a4 - 0x0;
        var _0x4a8c5b = _0x25f3a4[_0x25f3a4];
        return _0x4a8c5b;
    };
    
    return _0x4a8c(_0x4a8c5b, _0x3f4d28);
}

// 签名生成主函数
function generateSignature(url, userAgent) {
    try {
        // 基础参数
        var timestamp = Math.floor(Date.now() / 1000);
        var random = Math.random().toString(36).substr(2, 15);
        
        // URL参数解析
        var urlParams = {};
        if (url.indexOf('?') > -1) {
            var queryString = url.split('?')[1];
            var pairs = queryString.split('&');
            for (var i = 0; i < pairs.length; i++) {
                var pair = pairs[i].split('=');
                if (pair.length === 2) {
                    urlParams[pair[0]] = decodeURIComponent(pair[1]);
                }
            }
        }
        
        // 构建签名字符串
        var signStr = '';
        var keys = Object.keys(urlParams).sort();
        for (var j = 0; j < keys.length; j++) {
            if (signStr) signStr += '&';
            signStr += keys[j] + '=' + urlParams[keys[j]];
        }
        
        // 添加时间戳和随机数
        if (signStr) signStr += '&';
        signStr += 'timestamp=' + timestamp + '&random=' + random;
        
        // 简单的哈希算法
        var hash = 0;
        for (var k = 0; k < signStr.length; k++) {
            var char = signStr.charCodeAt(k);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // 转换为32位整数
        }
        
        // 生成最终签名
        var signature = Math.abs(hash).toString(16) + timestamp.toString(16);
        
        return {
            signature: signature,
            timestamp: timestamp,
            random: random
        };
        
    } catch (error) {
        console.error('签名生成错误:', error);
        return {
            signature: '',
            timestamp: Math.floor(Date.now() / 1000),
            random: Math.random().toString(36).substr(2, 15)
        };
    }
}

// 导出函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generateSignature: generateSignature,
        w_0x25f3: w_0x25f3
    };
}