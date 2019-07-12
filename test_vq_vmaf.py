import csv
import json
import os

def run(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

def vmaf_get(video_res, source_video, out_video):
    vmaf_folder = '/home/vmaf/vmaf-1.3.9'
    video_width = video_res.split('x')[0]
    video_height = video_res.split('x')[1]
    # get yuv and compare psnr
    source_yuv = source_video.split('.')[0] + '.yuv'
    if os.path.exists(source_yuv) :
        pass
    else:
        yuv_cmdline = 'ffmpeg -y -i {}  -c:v rawvideo -vsync 0 {}'.format(source_video, source_yuv)
        print(yuv_cmdline)
        run(yuv_cmdline)
    out_yuv = out_video.split('.')[0] + '.yuv'
    ffmpeg_yuv_cmd = 'ffmpeg -y -i {} -c:v rawvideo -vsync 0 {}'.format(out_video, out_yuv)
    print(ffmpeg_yuv_cmd)
    run(ffmpeg_yuv_cmd)
    
    vmaf_cmd = 'cd {};./run_vmaf yuv420p  {} {} {} {} --out-fmt json'.format(vmaf_folder, video_width, video_height , source_yuv, out_yuv)
    print(vmaf_cmd)
    vmaf_info = os.popen(vmaf_cmd).read()
    # print(vmaf_info)
    j = json.loads(vmaf_info)
    VMAF_score = j['aggregate']['VMAF_score']
    print('VMAF_score: {}'.format(VMAF_score))
    vmaf_log_csv_name = os.path.split(out_yuv)[0] + '/'+"vmaf_" + os.path.split(source_yuv)[1].split('.')[0] +'-'+ os.path.split(out_yuv)[1].split('.')[0] + '.csv'
    if os.path.exists(vmaf_log_csv_name):
        os.remove(vmaf_log_csv_name)
    with open(vmaf_log_csv_name, 'a') as out_fps:
        lists = j['frames']
        csv_write2 = csv.writer(out_fps,delimiter=',')
        csv_write2.writerow(["frameNum","VMAF_score"])
        for i in lists:
            csv_write2.writerow([i['frameNum'], i['VMAF_score']])
    os.remove(out_yuv)
    return VMAF_score
