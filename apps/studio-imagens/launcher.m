#import <Cocoa/Cocoa.h>
@interface StudioDelegate : NSObject <NSApplicationDelegate>
@end
@implementation StudioDelegate
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED,0), ^{
        NSString *root=@"/Users/alex/Documents/sunburst/Studio";
        NSTask *task=[NSTask new];
        task.executableURL=[NSURL fileURLWithPath:@"/opt/homebrew/bin/python3"];
        task.arguments=@[[root stringByAppendingPathComponent:@"boot.py"]];
        task.currentDirectoryURL=[NSURL fileURLWithPath:root];
        NSPipe *pipe=[NSPipe pipe];task.standardOutput=pipe;task.standardError=pipe;
        NSError *error=nil;
        BOOL launched=[task launchAndReturnError:&error];
        NSString *output=@"";
        if(launched){output=[[NSString alloc] initWithData:[pipe.fileHandleForReading readDataToEndOfFile] encoding:NSUTF8StringEncoding];[task waitUntilExit];}
        dispatch_async(dispatch_get_main_queue(), ^{
            if(launched && task.terminationStatus==0 && [output containsString:@"http://127.0.0.1:62028/"]){
                [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://127.0.0.1:62028/"]];
            } else {
                NSAlert *alert=[NSAlert new];alert.messageText=@"Não foi possível abrir o Sunburst Studio";
                alert.informativeText=launched?output:error.localizedDescription;[alert runModal];
            }
            [NSApp terminate:nil];
        });
    });
}
@end
int main(int argc,const char *argv[]){@autoreleasepool{NSApplication *app=[NSApplication sharedApplication];StudioDelegate *delegate=[StudioDelegate new];app.delegate=delegate;[app setActivationPolicy:NSApplicationActivationPolicyAccessory];[app run];}return 0;}
