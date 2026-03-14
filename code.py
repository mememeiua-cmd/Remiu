<?php
// Golike Tool - ĐA NỀN TẢNG (LinkedIn, Snapchat, Pinterest)
// Feature: Smart Delay + Auto Cancel Error
// Lên mâm cho sếp Quốc Anh

error_reporting(0);
date_default_timezone_set('Asia/Ho_Chi_Minh');
system('clear');

// --- CẤU HÌNH ---
$ua = "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36";
$t_value = "VFZSak1rMVVUWGxOUkVFeVRWRTlQUT09";
$MAX_ACC = 10;
$platforms = ['linkedin', 'snapchat', 'pinterest']; // Thêm bao nhiêu nền tảng vô đây cũng cân tất

echo "\033[1;33m--- TOOL GOLIKE ĐA HỆ ---\033[0m\n";
echo "Nhập số giây delay (Khuyến nghị 15-20s): ";
$input_delay = trim(fgets(STDIN));
$DELAY_MAC_DINH = intval($input_delay) > 0 ? intval($input_delay) : 15;

// --- CÁC HÀM HỖ TRỢ ---
function curl_get($url, $headers) {
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_CUSTOMREQUEST => "GET",
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_ENCODING => "",
    ]);
    $res = curl_exec($ch);
    curl_close($ch);
    return $res;
}

function curl_post($url, $headers, $data) {
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_POSTFIELDS => $data,
        CURLOPT_CUSTOMREQUEST => "POST",
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_ENCODING => "",
    ]);
    $res = curl_exec($ch);
    curl_close($ch);
    return $res;
}

// ==========================================================
// ===== QUẢN LÝ AUTH =====
// ==========================================================
$auth_history_file = ".golike_auth_multi.json";
$auth_list = [];

if (file_exists($auth_history_file)) {
    $saved_auths = json_decode(file_get_contents($auth_history_file), true);
    if (is_array($saved_auths) && count($saved_auths) > 0) {
        echo "Thấy " . count($saved_auths) . " Auth cũ. Dùng luôn (y), Thêm mới (n), Xóa sạch làm lại (d)?: ";
        $chon = strtolower(trim(fgets(STDIN)));
        if ($chon === 'y') $auth_list = array_slice($saved_auths, 0, $MAX_ACC);
        elseif ($chon === 'd') unlink($auth_history_file);
    }
}

if (empty($auth_list)) {
    echo "--- NHẬP AUTH (Max 10) - Gõ 'ok' để chạy ---\n";
    while (count($auth_list) < $MAX_ACC) {
        echo "Auth " . (count($auth_list) + 1) . "/$MAX_ACC: ";
        $authu_input = trim(fgets(STDIN));
        if (strtolower($authu_input) === 'ok') break;
        if (!empty($authu_input) && !in_array($authu_input, $auth_list)) $auth_list[] = $authu_input;
    }
    file_put_contents($auth_history_file, json_encode($auth_list));
    echo "Đã lưu " . count($auth_list) . " tài khoản.\n";
}

// ================================================
// ===== VÒNG LẶP VĨNH CỬU 24/7 =====
// ================================================
echo "Lên đồ! Đang chạy đa hệ...\n";
sleep(1);

while (true) {
    system('clear');
    echo ">>> BẮT ĐẦU VÒNG LẶP QUÉT JOB <<<\n";

    foreach ($auth_list as $account_index => $authu) {
        $tsm = ["Host: gateway.golike.net", "user-agent: $ua", "authorization: $authu", "origin: https://app.golike.net", "t: $t_value", "accept: application/json, text/plain, */*"];
        $tsm1 = ["Host: dev.golike.net", "user-agent: $ua", "authorization: $authu", "origin: https://app.golike.net", "t: $t_value", "content-type: application/json;charset=UTF-8"];

        echo "\n=== ACCOUNT " . ($account_index + 1) . "/" . count($auth_list) . " (..." . substr($authu, -8) . ") ===\n";

        // Quét từng nền tảng
        foreach ($platforms as $plat) {
            $plat_up = strtoupper($plat);
            echo "   [$plat_up] Đang lùng sục nick...\n";
            $nick = json_decode(curl_get("https://gateway.golike.net/api/{$plat}-account", $tsm), true);

            if (isset($nick['data']) && is_array($nick['data']) && count($nick['data']) > 0) {
                $active = range(0, count($nick['data']) - 1);

                while (count($active) > 0) {
                    foreach ($active as $k => $idx) {
                        $id = $nick['data'][$idx]['id'];
                        $ten = $nick['data'][$idx][$plat.'_username'] ?? $nick['data'][$idx]['username'] ?? 'NoName';

                        $job = json_decode(curl_get("https://dev.golike.net/api/advertising/publishers/{$plat}/jobs?account_id=$id&data=null", $tsm1), true);
                        if (!isset($job['data']['id'])) $job = json_decode(curl_get("https://gateway.golike.net/api/advertising/publishers/{$plat}/jobs?account_id=$id&data=null", $tsm), true);

                        if (!isset($job['data']['id'])) {
                            echo "   [SKIP] $ten: Cạn job $plat_up.\n";
                            unset($active[$k]);
                            continue;
                        }

                        $uid = $job['data']['id'];
                        $coin = $job['data']['price_after_cost'];

                        // Báo cáo hoàn thành
                        $res = curl_post("https://dev.golike.net/api/advertising/publishers/{$plat}/complete-jobs", $tsm1, json_encode(["ads_id" => $uid, "account_id" => $id, "async" => true, "data" => null]));
                        $nhan = json_decode($res, true);
                        $delay_nay = $DELAY_MAC_DINH;

                        if (($nhan['status'] ?? 0) == 200 || ($nhan['success'] ?? false)) {
                            echo "   [+] $plat_up | $ten | Húp +$coin lúa\n";
                        } else {
                            $msg = $nhan['message'] ?? "Lỗi lạ kì";
                            if (strpos($msg, 'Không thể báo cáo') !== false || strpos($msg, 'Vui lòng') !== false) {
                                echo "   [LỖI] Xịt job -> Tự động hủy...\n";
                                curl_post("https://dev.golike.net/api/advertising/publishers/{$plat}/skip-jobs", $tsm1, json_encode(["ads_id" => $uid, "account_id" => $id, "object_id" => $uid]));
                            } else {
                                echo "   [LỖI] $ten: $msg\n";
                            }
                            if (preg_match('/sau\s*(\d+)/i', $msg, $matches)) $delay_nay = intval($matches) + 2;
                        }

                        // Vòng lặp đếm ngược ngầu lòi
                        for($d = $delay_nay; $d > 0; $d--) {
                            echo "   > Đang chill chờ $d s...   \r";
                            sleep(1);
                        }
                        echo "                              \r";
                    }
                }
            } else {
                echo "   -> Ế, không có nick $plat_up nào active.\n";
            }
        } // Hết vòng lặp nền tảng

        echo "   Xong Account này, nghỉ 5s chuyển Acc...\n";
        sleep(5);
    }

    $time_nghi = rand(30, 60);
    echo "\nQuét xong một vòng lớn. Thở oxy $time_nghi giây rồi cày tiếp...\n";
    for($x = $time_nghi; $x > 0; $x--){
        echo " Hồi sinh sau: $x s   \r";
        sleep(1);
    }
}
