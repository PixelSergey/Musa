#!/usr/bin/python3
import pafy, vlc, requests, time, urllib3

urllib3.disable_warnings()

TIMEOUT = 20

with open("serverip.txt", "r") as f:
    SERVU = f"http://{f.readlines()[0].strip()}"

instance = vlc.Instance()
player = instance.media_player_new()


try:
    while True:
        if player.is_playing():
            continue

        print("Getting next song...")
        r = requests.post(SERVU + "/next/", verify=False)
        if not r.status_code == 200:
            print(f"Invalid response: {r.status_code}\n{r.text}")
            break
        
        url = r.text
        if url == "NULL":
            print(f"Nothing in queue, retrying in {TIMEOUT}s")
            time.sleep(TIMEOUT)
            continue
        
        print("Got URL", url)
        video = pafy.new(url)
        best = video.getbestaudio()
        playurl = best.url
        
        media = instance.media_new(playurl, ":no-video")
        media.get_mrl()
        player.set_media(media)
        player.play()

        time.sleep(10)

except KeyboardInterrupt:
    print("Stopping playback...")
    requests.post(SERVU + "/stop/", verify=False)
    print("Playback stopped")
